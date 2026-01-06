import os
import numpy as np
import pandas as pd


import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import pycountry

caminho_base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
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
st.markdown("Explore algumas perguntas sobre as Entregas da Amazon.")

st.markdown('---')

if not df.empty:
    atrasos_tempo = st.container()
    status_entrega = st.container()
    clima_atrasos = st.container()
    veiculo_entrega = st.container()
    atraso_area = st.container()

    with atrasos_tempo:
        df_atrasos = df[df['Delivery_Status'] == 'delay'].groupby('Order_Week')['Order_ID'].nunique().reset_index(name='Quantidade')


        fig = px.bar(
            df_atrasos,
            x='Order_Week',
            y='Quantidade',
            text='Quantidade',
            title='Os atrasos estão aumentando, diminuindo ou se mantendo estáveis ao longo das semanas?',
            # color=cor,
            color_discrete_sequence=['#F5A623']
        )

        fig.update_xaxes(
            type='category',
        )

        fig.update_traces(
            textfont_color="black",
        )

        fig.update_layout(
            font=dict(family="Arial", size=14),
            barmode='group',
            bargap=0.3,
            yaxis=dict(
                title="Quantidade de Pedidos",
                showgrid=True,
                gridcolor='dimgray',
                zeroline=True,
                zerolinecolor='dimgray',
                range=[0, df_atrasos['Quantidade'].max() * 1.4]
            ),
            xaxis=dict(
                title='Semanas'
            ),
            uniformtext_minsize=10,
            uniformtext_mode='show',
        )

        st.plotly_chart(fig, key='Os atrasos estão aumentando, diminuindo ou se mantendo estáveis ao longo das semanas?')

    with status_entrega:
        df_entregas = df.groupby(['Order_Week', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        fig = px.bar(
            df_entregas,
            x='Order_Week',
            y='Quantidade',
            text='Quantidade',
            title='Em quais semanas a proporção de atrasos foi mais crítica?',
            color='Delivery_Status',
            color_discrete_map={'ontime': '#4A90E2', 'delay': '#F5A623'}
        )

        fig.update_xaxes(
            type='category',
        )

        fig.update_traces(
            textposition='auto',
            # Garante que o texto não suma se estiver fora da área do gráfico
            cliponaxis=False,
        )

        fig.update_traces(
            name='No prazo',
            selector=dict(
                name='ontime'
            )
        )

        fig.update_traces(
            name='Atraso',
            selector=dict(
                name='delay'
            )
        )
        
        fig.for_each_trace(
            lambda t: t.update(
                textfont=dict(color="white") if t.name == "ontime" else dict(color="black"),
                insidetextanchor='middle', 
                textposition='auto'
            )
        )

        fig.update_layout(
            font=dict(
                family="Arial",
                size=14,
                color="black"
            ),
            bargap=0.2,
            yaxis=dict(
                title="Quantidade de Pedidos",
                showgrid=True,
                gridcolor='dimgray',
                zeroline=True,
                zerolinecolor='black',
                range=[0, df_entregas['Quantidade'].max() * 1.4]
            ),
            xaxis=dict(
                title='Semanas',
                automargin=True,
            ),
            uniformtext_minsize=10,
            uniformtext_mode='show',
        )

        st.plotly_chart(fig, key='Em quais semanas a proporção de atrasos foi mais crítica?')

    with clima_atrasos:
        df_risco = df.groupby(['Weather', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Qtd')
        df_risco['Total'] = df_risco.groupby('Weather')['Qtd'].transform('sum')
        df_risco['Taxa_Atraso'] = (df_risco['Qtd'] / df_risco['Total']) * 100

        df_atraso = df_risco[df_risco['Delivery_Status'] == 'delay'].sort_values('Taxa_Atraso', ascending=True)

        # Ordenar para que os climas com MAIOR taxa de atraso apareçam primeiro
        # ordem_risco = df_risco[df_risco['Delivery_Status'] == 'delay'].sort_values('Taxa_Atraso', ascending=False)['Weather'].tolist()

        # 2. Criação do Gráfico
        fig = px.bar(
            df_atraso, 
            y='Weather', 
            x='Taxa_Atraso', 
            color='Delivery_Status',
            orientation='h',
            title='Quais condições climáticas representam maior risco de atraso para a operação?',
            text=df_atraso['Taxa_Atraso'].apply(lambda x: f'{x:.1f}%'),
            # category_orders={"Weather": ordem_risco, "Delivery_Status": ["ontime", "delay"]},
            color_discrete_map={'ontime': '#4A90E2', 'delay': '#F5A623'}
        )

        # 3. Estilização para Resposta Executiva
        fig.update_layout(
            font=dict(family="Arial", size=14),
            # plot_bgcolor='white',
            bargap=0.2,
            xaxis=dict(
                title="Atraso (%)",
                ticksuffix="%",
                range=[0, 105],
                dtick=20,
                showgrid=True,
                gridcolor='dimgray'
            ),
            yaxis=dict(
                title='Clima'
            ),
            showlegend=False
        )

        fig.update_traces(
            textfont_color="black",
        )

        st.plotly_chart(fig, key='Quais condições climáticas representam maior risco de atraso para a operação?')
    
    with veiculo_entrega:
        df_veiculo = df.groupby(['Vehicle', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        # Criamos a base para a normalização (100%)
        df_veiculo['Total_Veiculo'] = df_veiculo.groupby('Vehicle')['Quantidade'].transform('sum')
        df_veiculo['Percentual'] = (df_veiculo['Quantidade'] / df_veiculo['Total_Veiculo']) * 100

        # 2. Criar o gráfico de barras empilhadas 100%
        fig = px.bar(
            df_veiculo, 
            x='Percentual', 
            y='Vehicle', 
            color='Delivery_Status',
            orientation='h',
            title='Qual tipo de veículo apresenta a maior taxa de atrasos?',
            text=df_veiculo['Percentual'].apply(lambda x: f'{x:.1f}%'),
            color_discrete_map={
                'ontime': '#4A90E2',
                'delay': '#F5A623'
            },
            category_orders={
                "Delivery_Status": ["ontime", "delay"]
            }
        )

        # 3. Aplicar a padronização de fonte e cores de texto
        fig.for_each_trace(lambda t: t.update(
            textfont=dict(color="white") if t.name == "ontime" else dict(color="black")
        ))

        # 4. Ajustes de Layout e Eixos
        fig.update_layout(
            font=dict(family="Arial", size=14, color="black"),
            barmode='stack',
            bargap=0.2,
            xaxis=dict(
                title="Proporção de Entregas (%)",
                ticksuffix="%",
                range=[0, 100.5],
                dtick=20,
                showgrid=True,
                gridcolor='dimgray',
                zeroline=True,
                zerolinecolor='black',
                zerolinewidth=2
            ),
            yaxis=dict(
                title='Veículos'
            ),
            legend_title_text='Status',
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )

        fig.update_traces(
            textposition='inside',
            cliponaxis=False
        )

        
        fig.update_traces(
            name='No prazo',
            selector=dict(
                name='ontime'
            )
        )

        fig.update_traces(
            name='Atraso',
            selector=dict(
                name='delay'
            )
        )

        st.plotly_chart(fig, key='Qual tipo de veículo apresenta a maior taxa de atrasos?')
    
    with atraso_area:
        df_area_abs = df.groupby(['Area', 'Delivery_Status'])['Order_ID'].nunique().reset_index(name='Quantidade')

        # 2. Ordenação para destacar as áreas com maior volume total (prioridade logística)
        df_area_abs['Total_Area'] = df_area_abs.groupby('Area')['Quantidade'].transform('sum')
        df_area_abs = df_area_abs.sort_values(by='Total_Area', ascending=False)

        # 3. Criar o gráfico de barras verticais empilhadas
        fig = px.bar(
            df_area_abs, 
            x='Area', 
            y='Quantidade', 
            color='Delivery_Status',
            title='Em quais áreas a empresa deveria priorizar ações para reduzir atrasos?',
            text='Quantidade',
            color_discrete_map={'ontime': '#4A90E2', 'delay': '#F5A623'},
            category_orders={"Delivery_Status": ["ontime", "delay"]},
        )

        # 4. Ajustes de Estilo e Fonte Uniforme
        fig.update_layout(
            font=dict(family="Arial", size=14, color="gray"),
            barmode='group',
            bargap=0.3,
            yaxis=dict(
                title="Quantidade de Pedidos",
                showgrid=True,
                gridcolor='dimgray',
                zeroline=True,
                zerolinecolor='dimgray',
                range=[0, df_area_abs['Quantidade'].max() * 1.4]
            ),
            xaxis=dict(
                title='Áreas'
            ),
            uniformtext_minsize=10,
            uniformtext_mode='show',
        )

        fig.update_traces(
            textposition='outside',
            texttemplate='%{text}',
            cliponaxis=False
        )

        fig.update_traces(
            name='No prazo',
            selector=dict(
                name='ontime'
            )
        )

        fig.update_traces(
            name='Atraso',
            selector=dict(
                name='delay'
            )
        )

        st.plotly_chart(fig, key='Em quais áreas a empresa deveria priorizar ações para reduzir atrasos?')

else:
    st.warning('A base de dados está vazia!!')