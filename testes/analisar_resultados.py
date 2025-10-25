#Script para gerar gráficos e análises dos resultados dos testes a partir do CSV
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import os

class AnalisadorResultados:
    def __init__(self, arquivo_csv='resultados/resultados_completos.csv'):
        self.arquivo_csv = arquivo_csv
        self.df = None
        self.carregar_resultados_csv()
        
    def carregar_resultados_csv(self):
        #Carrega os resultados dos testes do arquivo CSV
        try:
            self.df = pd.read_csv(self.arquivo_csv)
            # CSV carregado silenciosamente
        except FileNotFoundError:
            print(f"Arquivo CSV não encontrado: {self.arquivo_csv}")
            print("Execute primeiro os testes completos para gerar o arquivo CSV")
            self.df = None
        except Exception as e:
            print(f"Erro ao carregar CSV: {e}")
            self.df = None
    
    def gerar_todos_graficos(self):
        #Gera todos os gráficos de análise a partir do CSV
        if self.df is None or self.df.empty:
            print("Nenhum resultado disponível para análise")
            return
        
        #Configura o estilo dos gráficos
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        #Cria diretório para gráficos
        os.makedirs('resultados/graficos', exist_ok=True)
        
        # Gerando gráficos silenciosamente
        
        #Gráficos individuais
        self.plotar_throughput()
        self.plotar_tempo_resposta()
        self.plotar_taxa_sucesso()
        self.plotar_comparacao_escalabilidade()
        
        print("Gráficos salvos em resultados/graficos/")

    def plotar_throughput(self):
        #Plota gráfico de throughput - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            plt.figure(figsize=(10, 6))
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if dados_cenario.empty:
                plt.text(0.5, 0.5, f'Sem dados para cenário {cenarios_nomes[i]}', 
                        ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
                plt.title(f'Throughput - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
                plt.savefig(f'resultados/graficos/throughput_{cenario}.png', dpi=300, bbox_inches='tight')
                plt.close()
                continue
            
            dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
            dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
            
            if not dados_seq.empty:
                plt.plot(dados_seq['num_clientes'], dados_seq['throughput'], 
                        'o-', label='Sequencial', color='red', linewidth=2, markersize=8)
            
            if not dados_conc.empty:
                plt.plot(dados_conc['num_clientes'], dados_conc['throughput'], 
                        's-', label='Concorrente', color='blue', linewidth=2, markersize=8)
            
            plt.title(f'Throughput - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
            plt.xlabel('Número de Clientes', fontsize=12)
            plt.ylabel('Throughput (req/s)', fontsize=12)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xlim(left=0)
            plt.ylim(bottom=0)
            
            plt.tight_layout()
            plt.savefig(f'resultados/graficos/throughput_{cenario}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print("Gráficos de throughput salvos: throughput_rapido.png, throughput_medio.png, throughput_lento.png")

    def plotar_tempo_resposta(self):
        #Plota gráfico de tempo de resposta - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            plt.figure(figsize=(10, 6))
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if dados_cenario.empty:
                plt.text(0.5, 0.5, f'Sem dados para cenário {cenarios_nomes[i]}', 
                        ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
                plt.title(f'Tempo de Resposta - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
                plt.savefig(f'resultados/graficos/tempo_resposta_{cenario}.png', dpi=300, bbox_inches='tight')
                plt.close()
                continue
            
            dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
            dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
            
            if not dados_seq.empty:
                plt.plot(dados_seq['num_clientes'], dados_seq['tempo_medio_ms'], 
                        'o-', label='Sequencial', color='red', linewidth=2, markersize=8)
            
            if not dados_conc.empty:
                plt.plot(dados_conc['num_clientes'], dados_conc['tempo_medio_ms'], 
                        's-', label='Concorrente', color='blue', linewidth=2, markersize=8)
            
            plt.title(f'Tempo de Resposta - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
            plt.xlabel('Número de Clientes', fontsize=12)
            plt.ylabel('Tempo Médio de Resposta (ms)', fontsize=12)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xlim(left=0)
            plt.ylim(bottom=0)
            
            plt.tight_layout()
            plt.savefig(f'resultados/graficos/tempo_resposta_{cenario}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print("Gráficos de tempo de resposta salvos: tempo_resposta_rapido.png, tempo_resposta_medio.png, tempo_resposta_lento.png")

    def plotar_taxa_sucesso(self):
        #Plota gráfico de taxa de sucesso - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            plt.figure(figsize=(10, 6))
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if dados_cenario.empty:
                plt.text(0.5, 0.5, f'Sem dados para cenário {cenarios_nomes[i]}', 
                        ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
                plt.title(f'Taxa de Sucesso - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
                plt.savefig(f'resultados/graficos/taxa_sucesso_{cenario}.png', dpi=300, bbox_inches='tight')
                plt.close()
                continue
            
            dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
            dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
            
            if not dados_seq.empty:
                plt.plot(dados_seq['num_clientes'], dados_seq['taxa_sucesso'], 
                        'o-', label='Sequencial', color='red', linewidth=2, markersize=8)
            
            if not dados_conc.empty:
                plt.plot(dados_conc['num_clientes'], dados_conc['taxa_sucesso'], 
                        's-', label='Concorrente', color='blue', linewidth=2, markersize=8)
            
            plt.title(f'Taxa de Sucesso - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
            plt.xlabel('Número de Clientes', fontsize=12)
            plt.ylabel('Taxa de Sucesso (%)', fontsize=12)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xlim(left=0)
            plt.ylim(0, 105)
            
            #Linha de referência em 100%
            plt.axhline(y=100, color='green', linestyle='--', alpha=0.7, label='Meta 100%')
            
            plt.tight_layout()
            plt.savefig(f'resultados/graficos/taxa_sucesso_{cenario}.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        print("Gráficos de taxa de sucesso salvos: taxa_sucesso_rapido.png, taxa_sucesso_medio.png, taxa_sucesso_lento.png")
    
    def plotar_comparacao_escalabilidade(self):
        #Plota gráfico comparativo de escalabilidade - um gráfico geral
        plt.figure(figsize=(12, 8))
        
        cenarios = ['rapido', 'medio', 'lento']
        cores = ['green', 'orange', 'purple']
        
        for i, (cenario, cor) in enumerate(zip(cenarios, cores)):
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if not dados_cenario.empty:
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
                
                if not dados_seq.empty:
                    plt.plot(dados_seq['num_clientes'], dados_seq['throughput'], 
                           '--', label=f'Sequencial {cenario.capitalize()}', color=cor, alpha=0.7, linewidth=1)
                
                if not dados_conc.empty:
                    plt.plot(dados_conc['num_clientes'], dados_conc['throughput'], 
                           '-', label=f'Concorrente {cenario.capitalize()}', color=cor, linewidth=2, markersize=6)
        
        plt.title('Comparação de Escalabilidade - Throughput por Cenário', fontsize=16, fontweight='bold')
        plt.xlabel('Número de Clientes', fontsize=12)
        plt.ylabel('Throughput (req/s)', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/escalabilidade_comparativa.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfico de escalabilidade salvo: escalabilidade_comparativa.png")

if __name__ == "__main__":
    analisador = AnalisadorResultados()
    analisador.gerar_todos_graficos()
    
    print("\nGráficos gerados com sucesso!")
    print("Arquivos criados:")
    print("  - throughput_rapido.png, throughput_medio.png, throughput_lento.png")
    print("  - tempo_resposta_rapido.png, tempo_resposta_medio.png, tempo_resposta_lento.png")
    print("  - taxa_sucesso_rapido.png, taxa_sucesso_medio.png, taxa_sucesso_lento.png")
    print("  - escalabilidade_comparativa.png")
