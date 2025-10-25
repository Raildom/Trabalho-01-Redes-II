#Script para gerar gráficos e análises dos resultados dos testes a partir do CSV
#Inclui estatisticas com media e desvio padrao de multiplas execucoes
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo para evitar problemas de display
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime
import os

#Classe para cores no terminal
class Cores:
    VERDE = '\033[92m'    # Verde para sucesso
    VERMELHO = '\033[91m' # Vermelho para erro
    AMARELO = '\033[93m'  # Amarelo para aviso
    AZUL = '\033[94m'     # Azul para informação
    RESET = '\033[0m'     # Reset para cor normal

    @staticmethod
    def sucesso(texto):
        return f"{Cores.VERDE}[SUCESSO]{Cores.RESET} {texto}"
    
    @staticmethod
    def erro(texto):
        return f"{Cores.VERMELHO}[ERRO]{Cores.RESET} {texto}"
    
    @staticmethod
    def info(texto):
        return f"{Cores.AZUL}[INFO]{Cores.RESET} {texto}"

class AnalisadorResultados:
    def __init__(self, arquivo_csv='resultados/resultados_completos.csv'):
        self.arquivo_csv = arquivo_csv
        self.df = None
        self.carregar_resultados_csv()
        
    def carregar_resultados_csv(self):
        #Carrega os resultados dos testes do arquivo CSV
        try:
            self.df = pd.read_csv(self.arquivo_csv)
            print(Cores.info(f"Dados carregados: {len(self.df)} registros encontrados"))
        except FileNotFoundError:
            print(Cores.erro(f"Arquivo CSV não encontrado: {self.arquivo_csv}"))
            print("Execute primeiro os testes completos para gerar o arquivo CSV")
            self.df = None
        except Exception as e:
            print(Cores.erro(f"Erro ao carregar CSV: {e}"))
            self.df = None
    
    def gerar_todos_graficos(self):
        #Gera todos os gráficos de análise a partir do CSV com barras de erro
        if self.df is None or self.df.empty:
            print(Cores.erro("Nenhum resultado disponível para análise"))
            return
        
        print(Cores.info("Configurando estilo dos gráficos..."))
        #Configura o estilo dos gráficos
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        
        #Cria diretório para gráficos
        os.makedirs('resultados/graficos', exist_ok=True)
        
        print(Cores.info("Gerando gráficos..."))
        
        #Gráficos individuais com barras de erro
        print(Cores.info("  • Plotando throughput..."))
        self.plotar_throughput_estatistico()
        
        print(Cores.info("  • Plotando tempo de resposta..."))
        self.plotar_tempo_resposta_estatistico()
        
        print(Cores.info("  • Plotando taxa de sucesso..."))
        self.plotar_taxa_sucesso_estatistico()
        
        print(Cores.info("  • Plotando comparação de escalabilidade..."))
        self.plotar_comparacao_escalabilidade_estatistico()
        
        print(Cores.sucesso("Gráficos com estatísticas salvos em resultados/graficos/"))

    def plotar_throughput_estatistico(self):
        #Plota gráfico de throughput com barras de erro - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        try:
            for i, cenario in enumerate(cenarios):
                plt.figure(figsize=(12, 8))
                dados_cenario = self.df[self.df['cenario'] == cenario]
                
                print(Cores.info(f"    - Processando cenário {cenarios_nomes[i]}: {len(dados_cenario)} registros"))
                
                if dados_cenario.empty:
                    plt.text(0.5, 0.5, f'Sem dados para cenário {cenarios_nomes[i]}', 
                            ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
                    plt.title(f'Throughput - Cenário {cenarios_nomes[i]}', fontsize=16, fontweight='bold')
                    plt.savefig(f'resultados/graficos/throughput_{cenario}.png', dpi=300, bbox_inches='tight')
                    plt.close()
                    continue
                
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
                
                print(Cores.info(f"      Sequencial: {len(dados_seq)} registros, Concorrente: {len(dados_conc)} registros"))
                
                if not dados_seq.empty:
                    plt.errorbar(dados_seq['num_clientes'], dados_seq['throughput_media'], 
                               yerr=dados_seq['throughput_desvio'], 
                               fmt='o-', label='Sequencial', color='red', linewidth=2, 
                               markersize=8, capsize=5, capthick=2)
                
                if not dados_conc.empty:
                    plt.errorbar(dados_conc['num_clientes'], dados_conc['throughput_media'], 
                               yerr=dados_conc['throughput_desvio'],
                               fmt='s-', label='Concorrente', color='blue', linewidth=2, 
                               markersize=8, capsize=5, capthick=2)
                
                execucoes = self.df['execucoes'].iloc[0] if not self.df.empty else 10
                plt.title(f'Throughput - Cenário {cenarios_nomes[i]}\n(Média +/- Desvio Padrão de {execucoes} execuções)', 
                         fontsize=16, fontweight='bold')
                plt.xlabel('Número de Clientes', fontsize=12)
                plt.ylabel('Throughput (req/s)', fontsize=12)
                plt.legend(fontsize=12)
                plt.grid(True, alpha=0.3)
                plt.xlim(left=0)
                plt.ylim(bottom=0)
                
                plt.tight_layout()
                plt.savefig(f'resultados/graficos/throughput_{cenario}.png', dpi=300, bbox_inches='tight')
                plt.close()
                
        except Exception as e:
            print(Cores.erro(f"Erro ao plotar throughput: {e}"))

    def plotar_tempo_resposta_estatistico(self):
        #Plota gráfico de tempo de resposta com barras de erro - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            plt.figure(figsize=(12, 8))
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
                plt.errorbar(dados_seq['num_clientes'], dados_seq['tempo_resposta_media'], 
                           yerr=dados_seq['tempo_resposta_desvio'],
                           fmt='o-', label='Sequencial', color='red', linewidth=2, 
                           markersize=8, capsize=5, capthick=2)
            
            if not dados_conc.empty:
                plt.errorbar(dados_conc['num_clientes'], dados_conc['tempo_resposta_media'], 
                           yerr=dados_conc['tempo_resposta_desvio'],
                           fmt='s-', label='Concorrente', color='blue', linewidth=2, 
                           markersize=8, capsize=5, capthick=2)
            
            execucoes = self.df['execucoes'].iloc[0] if not self.df.empty else 10
            plt.title(f'Tempo de Resposta - Cenário {cenarios_nomes[i]}\n(Média +/- Desvio Padrão de {execucoes} execuções)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Número de Clientes', fontsize=12)
            plt.ylabel('Tempo Médio de Resposta (ms)', fontsize=12)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xlim(left=0)
            plt.ylim(bottom=0)
            
            plt.tight_layout()
            plt.savefig(f'resultados/graficos/tempo_resposta_{cenario}.png', dpi=300, bbox_inches='tight')
            plt.close()

    def plotar_taxa_sucesso_estatistico(self):
        #Plota gráfico de taxa de sucesso com barras de erro - um gráfico por cenário
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            plt.figure(figsize=(12, 8))
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
                plt.errorbar(dados_seq['num_clientes'], dados_seq['taxa_sucesso_media'], 
                           yerr=dados_seq['taxa_sucesso_desvio'],
                           fmt='o-', label='Sequencial', color='red', linewidth=2, 
                           markersize=8, capsize=5, capthick=2)
            
            if not dados_conc.empty:
                plt.errorbar(dados_conc['num_clientes'], dados_conc['taxa_sucesso_media'], 
                           yerr=dados_conc['taxa_sucesso_desvio'],
                           fmt='s-', label='Concorrente', color='blue', linewidth=2, 
                           markersize=8, capsize=5, capthick=2)
            
            execucoes = self.df['execucoes'].iloc[0] if not self.df.empty else 10
            plt.title(f'Taxa de Sucesso - Cenário {cenarios_nomes[i]}\n(Média +/- Desvio Padrão de {execucoes} execuções)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Número de Clientes', fontsize=12)
            plt.ylabel('Taxa de Sucesso (%)', fontsize=12)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.xlim(left=0)
            plt.ylim(0, 105)  # 0-100% com margem
            
            plt.tight_layout()
            plt.savefig(f'resultados/graficos/taxa_sucesso_{cenario}.png', dpi=300, bbox_inches='tight')
            plt.close()

    def plotar_comparacao_escalabilidade_estatistico(self):
        #Plota gráfico de comparação de escalabilidade com barras de erro
        plt.figure(figsize=(14, 10))
        
#Calcular throughput médio por cenário para comparação
        throughput_seq = []
        throughput_conc = []
        throughput_seq_err = []
        throughput_conc_err = []
        labels = []
        
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_nomes = ['Rápido', 'Médio', 'Lento']
        
        for i, cenario in enumerate(cenarios):
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if not dados_cenario.empty:
#Calcular throughput médio geral para cada servidor neste cenário
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial']
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente']
                
                if not dados_seq.empty:
                    seq_media = dados_seq['throughput_media'].mean()
                    seq_desvio = np.sqrt((dados_seq['throughput_desvio']**2).mean())  # Desvio médio quadrático
                else:
                    seq_media = seq_desvio = 0
                    
                if not dados_conc.empty:
                    conc_media = dados_conc['throughput_media'].mean()
                    conc_desvio = np.sqrt((dados_conc['throughput_desvio']**2).mean())  # Desvio médio quadrático
                else:
                    conc_media = conc_desvio = 0
                
                throughput_seq.append(seq_media)
                throughput_conc.append(conc_media)
                throughput_seq_err.append(seq_desvio)
                throughput_conc_err.append(conc_desvio)
                labels.append(cenarios_nomes[i])
        
        if throughput_seq or throughput_conc:
            x = np.arange(len(labels))
            width = 0.35
            
            plt.bar(x - width/2, throughput_seq, width, yerr=throughput_seq_err,
                   label='Sequencial', color='red', alpha=0.7, capsize=5)
            plt.bar(x + width/2, throughput_conc, width, yerr=throughput_conc_err,
                   label='Concorrente', color='blue', alpha=0.7, capsize=5)
            
            execucoes = self.df['execucoes'].iloc[0] if not self.df.empty else 10
            plt.title(f'Comparação de Escalabilidade entre Servidores\n(Throughput Médio +/- Desvio Padrão de {execucoes} execuções)', 
                     fontsize=16, fontweight='bold')
            plt.xlabel('Cenário de Processamento', fontsize=12)
            plt.ylabel('Throughput Médio (req/s)', fontsize=12)
            plt.xticks(x, labels)
            plt.legend(fontsize=12)
            plt.grid(True, alpha=0.3, axis='y')
            plt.ylim(bottom=0)
        else:
            plt.text(0.5, 0.5, 'Sem dados para comparação', 
                    ha='center', va='center', transform=plt.gca().transAxes, fontsize=14)
            plt.title('Comparação de Escalabilidade entre Servidores', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/comparacao_throughput.png', dpi=300, bbox_inches='tight')
        plt.close()

def main():
    """Função principal para executar a análise"""
    analisador = AnalisadorResultados()
    analisador.gerar_todos_graficos()

if __name__ == "__main__":
    main()
