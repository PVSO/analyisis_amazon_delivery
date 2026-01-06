import os
import numpy as np
import pandas as pd


import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry

caminho_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
dataset = os.path.join(caminho_base, 'data', 'raw', 'amazon_delivery_dados_alunos.xlsx')

@st.cache_data
def carregar_dados(caminho):
    return pd.read_excel(caminho)

df = carregar_dados(dataset)

st.set_page_config(
    page_title='Dashboard da análise de Entregas da Amazon',
    page_icon='📚',
    layout='wide',
    initial_sidebar_state='collapsed'
)

st.title("🎲 Dashboard de análise de Entregas da Amazon")
st.markdown("Explore as Entregas da Amazon.")

st.markdown('---')

st.subheader('Métricas gerais')

def card_formatado(titulo, valor, altura=100, font_size=40):
    html = f"""
    <div style="
        border: 1px var(--secondary-background-color) #808080;
        padding: 15px;
        border-radius: 2px;
        height: {altura}px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 10px;
        background-color: var(--background-color);
    ">
        <div style="
        font-size: 16px; color: var(--text-color); margin-bottom: 5px; width: 100%; text-align: center;">{titulo}</div>
        <div style="font-size: {font_size}px; font-weight: var(--font); color: var(--text-color); width: 100%; text-align: center;">{valor}</div>
    </div>
    """
    return html

if not df.empty:
    # 1. Cálculos
    total_entregas = df.shape[0]
    tempo_medio_entrega = round(df['Delivery_Time'].mean(), 0)
    tempo_min_entrega = round(df['Delivery_Time'].min(), 0)
    tempo_max_entrega = round(df['Delivery_Time'].max(), 0)
    tempo_std_entrega = round(df['Delivery_Time'].std(), 0)

    # 2. Organização das Colunas Principais
    # Dividimos em duas grandes áreas: Gráfico de Meta vs Seção de Tempo
    col_esquerda, col_direita = st.columns([1, 1.2])

    with col_esquerda:
        st.markdown("### Meta das Entregas")
        valor_grafico = total_entregas / 1000
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor_grafico,
            number = {'suffix': " mil", 'font': {'size': 45}, 'valueformat': ".1f"},
            title = {'text': "Order_ID", 'font': {'size': 18}},
            gauge = {
                'axis': {'range': [0, 50.0], 'visible': False},
                'bar': {'color': "#4285F4"},
                'bgcolor': "#E0E0E0",
                'borderwidth': 0,
            }
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, width='stretch')

    with col_direita:
        st.markdown("### Tempo de Entrega")
        
        # Sub-colunas para criar o efeito: 1 grande à esquerda e 3 pequenos à direita
        col_med, col_lista = st.columns([1, 1])
        
        with col_med:
            # Tempo Médio (Grande)
            st.markdown(card_formatado("Tempo Médio de Entrega", int(tempo_medio_entrega), altura=320, font_size=80), unsafe_allow_html=True)
            
        with col_lista:
            # Mínimo, Máximo e Desvio (Pequenos empilhados)
            st.markdown(card_formatado("Tempo Mínimo", int(tempo_min_entrega), altura=100), unsafe_allow_html=True)
            st.markdown(card_formatado("Tempo Máximo", int(tempo_max_entrega), altura=100), unsafe_allow_html=True)
            st.markdown(card_formatado("Desvio Padrão", int(tempo_std_entrega), altura=100), unsafe_allow_html=True)

    st.markdown('---')

    graf_entregas_status = st.container()

    atraso_regiao, atraso_clima = st.columns(2)
    atraso_veiculo, atraso_trafego = st.columns(2)
    mapa_calor, atraso_idade = st.columns(2)
    entrega_categoria, agent_rating = st.columns(2)

    with graf_entregas_status:
        # Qual a quantidade de entregas com e sem atraso?
        df_grafico = df.groupby(['Order_Week', 'Delivery_Status'])['Order_ID'].nunique().reset_index()

        # 3. Mapear as cores exatas da imagem
        cores = {'ontime': '#4A90E2', 'delay': '#F5A623'}

        # 4. Criar o gráfico de área
        fig = px.line(
            df_grafico,
            x='Order_Week', 
            y='Order_ID', 
            color='Delivery_Status',
            color_discrete_map=cores,
            title='Entrega por Status',
            category_orders={
                "Delivery_Status": ["on_time", "delay"]
            },
            labels={
                'Order_Week': 'Semanas',
                'Order_ID': 'Quantidade de Pedidos'
            },
        )

        # 5. Adicionar os marcadores e rótulos de dados (os números sobre as linhas)
        fig.update_traces(
            mode="markers+lines+text", 
            texttemplate='%{y}', 
            textposition="top center",
        )

        # 6. Ajustes estéticos de layout
        fig.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            xaxis=dict(
                type='category'
            ),
            yaxis=dict(
                gridcolor='lightgrey',
                showgrid=True,
                # range=[0, gasto_etario['Gasto-Cliente'].max() * 1.2],
                zeroline=True,
                zerolinecolor='black',
            )
        )

        st.plotly_chart(fig, key='Qual a quantidade de entregas com e sem atraso?')

    with atraso_regiao:
        # Em quais região/área o atraso se concentra?

        df_area = df.groupby(['Area', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        cores = {'ontime': '#4A90E2', 'delay': '#F5A623'}

        # 4. Criar o gráfico de área
        df_area['Total_Area'] = df_area.groupby('Area')['Quantidade'].transform('sum')
        # Calculamos quanto o status representa do total daquela área
        df_area['Percentual'] = (df_area['Quantidade'] / df_area['Total_Area']) * 100

        areas = [
            'Metropolitian', 'Urban', 'Other', 'Semi-Urban'
        ]

        # 3. Criar o gráfico usando a coluna 'Percentual' no eixo Y
        fig = px.bar(
            df_area, 
            x='Area', 
            y='Percentual', 
            color='Delivery_Status',
            title='% Atraso por Área',
            text=df_area['Quantidade'],
            color_discrete_map={
                'ontime': '#4A90E2',
                'delay': '#F5A623'
            },
            category_orders={
                "Area": areas,
                "Delivery_Status": ["ontime", "delay"] # Altera qual cor fica embaixo/em cima
            }
        )

        fig.update_traces(
            textposition='inside',      # Força o texto para dentro da barra
            textangle=0,
            # insidetextanchor='center',  # Centraliza o texto na fatia
            textfont_size=12,           # Define um tamanho fixo
            textfont_color='white',     # Cor branca para contraste (ou black se preferir)
            cliponaxis=False            # Impede que o texto seja cortado nas bordas
        )

        fig.for_each_trace(lambda t: t.update(
            textfont=dict(color="white", size=12) if t.name == "ontime" 
            else dict(color="black", size=12)
        ))

        # 4. Ajustes para "extender" e colar as barras
        fig.update_layout(
            barmode='stack', # Empilha as barras para somarem 100%
            bargap=0.1,      # Deixa as barras mais largas
            plot_bgcolor='white',
            yaxis=dict(
                ticksuffix="%",
                range=[0, df_area['Percentual'].max() * 1.2],
                showgrid=True,
                gridcolor='black',
                gridwidth=1,
                zeroline=True,             # <-- mostra a linha do eixo 0
                zerolinecolor='black',     # <-- define a cor
                zerolinewidth=1.5,
            ) # Garante que o eixo Y vá até 100
        )

        st.plotly_chart(fig, key='Em quais região/área o atraso se concentra?')

    with atraso_clima:
        df_clima = df.groupby(['Weather', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        df_clima['Total_Area'] = df_clima.groupby('Weather')['Quantidade'].transform('sum')
        # Calculamos quanto o status representa do total daquela área
        df_clima['Percentual'] = (df_clima['Quantidade'] / df_clima['Total_Area']) * 100

        clima = [
            'Fog', 'Stormy','Cloudy', 'Sandstorms', 'Windy', 'Sunny', 'NaN'
        ]

        # cores_texto = ['white' if status == 'ontime' else 'black' for status in df_clima['Delivery_Status']]

        fig = px.bar(
            df_clima, 
            x='Percentual', 
            y='Weather', 
            color='Delivery_Status',
            title='% Atraso por Clima',
            text=df_clima['Quantidade'], # Rótulo com %
            color_discrete_map={
                'ontime': '#4A90E2',
                'delay': '#F5A623'
            },
            # orientation='h'
            category_orders={
                "Weather": clima,
                "Delivery_Status": ["ontime", "delay"] # Altera qual cor fica embaixo/em cima
            }
        )

        fig.for_each_trace(lambda t: t.update(textfont_color="white") if t.name == "ontime" else t.update(textfont_color="black"))

        fig.update_xaxes(
            tickformat=".0f",        # Remove casas decimais dos números do eixo
            ticksuffix="%",          # Adiciona o símbolo de %
            range=[0, 101.1],          # Garante que o eixo termine em 100%,
            # tick0=0,
            dtick=10,
            # tickvals=[0, 20, 40, 60, 80, 100],
            showline=True,           # Mostra a linha do eixo
            linewidth=1, 
            linecolor='lightgrey', 
            showgrid=True,           # Ativa as linhas de grade verticais
            gridcolor='Black',
            zeroline=True,           # Ativa a linha do "zero"
            zerolinewidth=2, 
            zerolinecolor='grey',     # Cor da linha vertical inicial (Y-axis line)
            title_text=""
        )

        fig.update_yaxes(
            showline=True, 
            linewidth=1, 
            linecolor='Black',
            title_text=""            # Remove o título "Weather" para limpar o visual
        )

        fig.update_traces(
            textposition='inside',
            texttemplate='%{text}',  # Garante que use o valor passado em 'text' (Quantidade)
            insidetextanchor='end',  # Alinha o texto à direita dentro da barra (opcional)
        )

        st.plotly_chart(fig, key='Em quais clima o atraso se concentra?')

    with atraso_veiculo:
        df_trafego = df.groupby(['Traffic', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        df_trafego['Total_Area'] = df_trafego.groupby('Traffic')['Quantidade'].transform('sum')
        # Calculamos quanto o status representa do total daquela área
        df_trafego['Percentual'] = (df_trafego['Quantidade'] / df_trafego['Total_Area']) * 100

        trafego = [
            'Low', 'Jam', 'Medium', 'High'
        ]

        fig = px.bar(
            df_trafego, 
            x='Percentual', 
            y='Traffic', 
            color='Delivery_Status',
            title='% Atraso por Tráfego',
            text=df_trafego['Quantidade'], # Rótulo com %
            color_discrete_map={'ontime': '#4A90E2', 'delay': '#F5A623'},
            # orientation='h'
            category_orders={
                "Traffic": trafego,
                "Delivery_Status": ["ontime", "delay"] # Altera qual cor fica embaixo/em cima
            }
        )

        fig.for_each_trace(lambda t: t.update(textfont_color="white") if t.name == "ontime" else t.update(textfont_color="black"))

        fig.update_xaxes(
            tickformat=".0f",        # Remove casas decimais dos números do eixo
            ticksuffix="%",          # Adiciona o símbolo de %
            range=[0, 101.1],          # Garante que o eixo termine em 100%,
            # tick0=0,
            dtick=10,
            # tickvals=[0, 20, 40, 60, 80, 100],
            showline=True,           # Mostra a linha do eixo
            linewidth=1, 
            linecolor='lightgrey', 
            showgrid=True,           # Ativa as linhas de grade verticais
            gridcolor='Black',
            zeroline=True,           # Ativa a linha do "zero"
            zerolinewidth=2, 
            zerolinecolor='grey',     # Cor da linha vertical inicial (Y-axis line)
            title_text=""
        )

        fig.update_yaxes(
            showline=True, 
            linewidth=1, 
            linecolor='Black',
            title_text=""            # Remove o título "Weather" para limpar o visual
        )

        fig.update_traces(
            textposition='inside',
            texttemplate='%{text}',  # Garante que use o valor passado em 'text' (Quantidade)
            insidetextanchor='end',  # Alinha o texto à direita dentro da barra (opcional)
        )

        st.plotly_chart(fig, key='Em quais tráfego o atraso se concentra?')

    with atraso_trafego:
        df_veiculo = df.groupby(['Vehicle', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        df_veiculo['Total_Area'] = df_veiculo.groupby('Vehicle')['Quantidade'].transform('sum')
        # Calculamos quanto o status representa do total daquela área
        df_veiculo['Percentual'] = (df_veiculo['Quantidade'] / df_veiculo['Total_Area']) * 100

        veiculo = [
            'motorcycle', 'scooter', 'van', 'bicycle'
        ]

        fig = px.bar(
            df_veiculo, 
            x='Percentual', 
            y='Vehicle', 
            color='Delivery_Status',
            title='% Atraso por Veículo',
            text=df_veiculo['Quantidade'], # Rótulo com %
            color_discrete_map={'ontime': '#4A90E2', 'delay': '#F5A623'},
            # orientation='h'
            category_orders={
                "Vehicle": veiculo,
                "Delivery_Status": ["ontime", "delay"] # Altera qual cor fica embaixo/em cima
            }
        )
        fig.for_each_trace(lambda t: t.update(textfont_color="white") if t.name == "ontime" else t.update(textfont_color="black"))

        fig.update_xaxes(
            tickformat=".0f",        # Remove casas decimais dos números do eixo
            ticksuffix="%",          # Adiciona o símbolo de %
            range=[0, 101.1],          # Garante que o eixo termine em 100%,
            # tick0=0,
            dtick=10,
            # tickvals=[0, 20, 40, 60, 80, 100],
            showline=True,           # Mostra a linha do eixo
            linewidth=1, 
            linecolor='lightgrey', 
            showgrid=True,           # Ativa as linhas de grade verticais
            gridcolor='Black',
            zeroline=True,           # Ativa a linha do "zero"
            zerolinewidth=2, 
            zerolinecolor='grey',     # Cor da linha vertical inicial (Y-axis line)
            title_text=""
        )

        fig.update_yaxes(
            showline=True, 
            linewidth=1, 
            linecolor='Black',
            title_text=""            # Remove o título "Weather" para limpar o visual
        )

        fig.update_traces(
            textposition='inside',
            texttemplate='%{text}',  # Garante que use o valor passado em 'text' (Quantidade)
            insidetextanchor='end',  # Alinha o texto à direita dentro da barra (opcional)
        )

        st.plotly_chart(fig, key='Em quais veículo o atraso se concentra?')

    with mapa_calor:
        pivot_clima = df.pivot_table(index=['Area', 'Weather', 'Vehicle'], 
                             columns='Delivery_Status', 
                             values='Order_ID',
                             aggfunc='count',
                             fill_value=0
                             )

        # Aplicar o mapa de calor com cores verdes (mais alto = melhor)
        pivot_clima_estilo = pivot_clima.style \
            .set_caption("Status de Entrega por Clima") \
            .background_gradient(cmap='RdYlGn', axis=None) \
            .format("{:.2f}") # Opcional: formata para 2 casas decimais

        st.header('Status de Entrega por Clima')
        st.dataframe(pivot_clima_estilo)

    with atraso_idade:
        tabela_bolhas = df.groupby('Delivery_Status').agg({
            'Agent_Age': 'mean',
            'Delivery_Time': 'mean',
            'Order_ID': 'count'
        }).reset_index()

        # Renomeando para facilitar a leitura no gráfico
        tabela_bolhas.columns = ['Status', 'Idade_Media', 'Tempo_Medio', 'Total_Pedidos']

        fig = px.scatter(
            tabela_bolhas,
            x='Idade_Media',
            y='Tempo_Medio',
            size='Total_Pedidos',      # O tamanho da bolha depende do volume de pedidos
            color='Status',            # Cor baseada no status
            text='Status',             # Texto dentro/sobre a bolha
            labels={
                'Idade_Media': 'Agent_Age',
                'Tempo_Medio': 'Delivery_Time'
            },
            range_x=[20, 38],          # Ajuste conforme a imagem (20 a 38)
            range_y=[25, 275],         # Ajuste conforme a imagem (até 250+)
            title="Atraso Médio por Idade"
        )

        # Ajustes estéticos para ficar idêntico à imagem
        fig.update_traces(
            textposition='top center', 
            marker=dict(sizeref=2.*max(tabela_bolhas['Total_Pedidos'])/(60**2), opacity=0.6)
        )

        # Deixar o fundo branco com linhas de grade (estilo Looker/Google)
        fig.update_layout(
            plot_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgrey'),
            yaxis=dict(
                showgrid=True,
                gridcolor='lightgrey',
                gridwidth=1,
                zeroline=True,             # <-- mostra a linha do eixo 0
                zerolinecolor='black',     # <-- define a cor
                zerolinewidth=1.5,
            ),
            showlegend=True
        )

        st.plotly_chart(fig, key='Existe relação com idade média do entregador?')

    with entrega_categoria:
        categorias_manter = [
            'Electronics', 'Books', 'Jewelry', 'Toys', 'Skincare', 
            'Snacks', 'Outdoors', 'Apparel', 'Sports'
        ]

        # Criar uma cópia da coluna para não estragar os dados originais
        df['Category_Grouped'] = df['Category'].apply(lambda x: x if x in categorias_manter else 'Outros')

        # 2. Gerar a tabela para o gráfico usando a nova coluna
        tabela_categoria = df.groupby('Category_Grouped')['Order_ID'].count().reset_index()
        tabela_categoria.columns = ['Categoria', 'Qtd Entregas']

        tabela_categoria['ordem_aux'] = tabela_categoria['Categoria'].apply(lambda x: 0 if x == 'Outros' else 1)
        tabela_categoria = tabela_categoria.sort_values(by=['ordem_aux', 'Qtd Entregas'], ascending=[True, False])

        fig = px.pie(
            tabela_categoria,
            names='Categoria',
            values='Qtd Entregas',
            title='Entregas por Categoria',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=.5
        )

        fig.update_traces(
            rotation=200, 
            direction='clockwise', 
            textinfo='percent'
        )

        st.plotly_chart(fig, key='Como é a distribuição das entregas por categoria?')

    with agent_rating:
        pivot_rating = df.pivot_table(index=['Area', 'Vehicle'], 
                             columns='Delivery_Status', 
                             values='Agent_Rating',
                             aggfunc='mean',
                             fill_value=0
                             )

        # Aplicar o mapa de calor com cores verdes (mais alto = melhor)
        pivot_rating_estilo = pivot_rating.style \
            .set_caption("Avaliações médias das entregas com e sem atraso") \
            .background_gradient(cmap='RdYlGn', axis=None) \
            .format("{:.2f}") # Opcional: formata para 2 casas decimais
        
        st.header('Avaliações médias das entregas com e sem atraso')
        st.dataframe(pivot_rating_estilo)

else:
    st.warning('A base de dados está vazia!!')

st.markdown('---')