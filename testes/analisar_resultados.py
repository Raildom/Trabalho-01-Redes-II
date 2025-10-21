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
            print(f"Resultados CSV carregados de {self.arquivo_csv}")
            print(f"Dados carregados: {len(self.df)} registros")
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
        
        #Cria diretório para gráficos
        os.makedirs('resultados/graficos', exist_ok=True)
        
        print("Gerando gráficos a partir do CSV...")
        
        #Comparação de throughput
        self.grafico_comparacao_throughput()
        
        #Comparação de tempo de resposta
        self.grafico_comparacao_tempo_resposta()
        
        #Taxa de sucesso
        self.grafico_comparacao_taxa_sucesso()
        
        #Análise de escalabilidade
        self.grafico_analise_escalabilidade()
        
        print("Gráficos salvos em resultados/graficos/")

    def grafico_comparacao_throughput(self):
        #Gráfico de comparação de throughput
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_labels = ['Rápido', 'Médio', 'Lento']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Comparação de Throughput entre Servidores', fontsize=16, fontweight='bold')
        
        for i, cenario in enumerate(cenarios):
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if not dados_cenario.empty:
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
                
                if not dados_seq.empty and not dados_conc.empty:
                    x = np.array(dados_seq['num_clientes'])
                    throughput_seq = dados_seq['throughput']
                    throughput_conc = dados_conc['throughput']
                    
                    axes[i].bar(x - 0.2, throughput_seq, 0.4, label='Sequencial', color='lightcoral', alpha=0.8)
                    axes[i].bar(x + 0.2, throughput_conc, 0.4, label='Concorrente', color='lightblue', alpha=0.8)
                    
                    axes[i].set_title(f'Cenário {cenarios_labels[i]}')
                    axes[i].set_xlabel('Número de Clientes')
                    axes[i].set_ylabel('Throughput (req/s)')
                    axes[i].legend()
                    axes[i].grid(True, alpha=0.3)
                    axes[i].set_xticks(x)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/comparacao_throughput.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfico de throughput salvo: comparacao_throughput.png")

    def grafico_comparacao_tempo_resposta(self):
        #Gráfico de comparação de tempo de resposta
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_labels = ['Rápido', 'Médio', 'Lento']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Comparação de Tempo de Resposta entre Servidores', fontsize=16, fontweight='bold')
        
        for i, cenario in enumerate(cenarios):
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if not dados_cenario.empty:
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
                
                if not dados_seq.empty and not dados_conc.empty:
                    x = np.array(dados_seq['num_clientes'])
                    tempos_seq = dados_seq['tempo_medio_ms']
                    tempos_conc = dados_conc['tempo_medio_ms']
                    
                    axes[i].bar(x - 0.2, tempos_seq, 0.4, label='Sequencial', color='lightcoral', alpha=0.8)
                    axes[i].bar(x + 0.2, tempos_conc, 0.4, label='Concorrente', color='lightblue', alpha=0.8)
                    
                    axes[i].set_title(f'Cenário {cenarios_labels[i]}')
                    axes[i].set_xlabel('Número de Clientes')
                    axes[i].set_ylabel('Tempo Médio (ms)')
                    axes[i].legend()
                    axes[i].grid(True, alpha=0.3)
                    axes[i].set_xticks(x)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/comparacao_tempo_resposta.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfico de tempo de resposta salvo: comparacao_tempo_resposta.png")

    def grafico_comparacao_taxa_sucesso(self):
        #Gráfico de comparação de taxa de sucesso
        cenarios = ['rapido', 'medio', 'lento']
        cenarios_labels = ['Rápido', 'Médio', 'Lento']
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.suptitle('Análise de Taxa de Sucesso por Cenário', fontsize=16, fontweight='bold')
        
        for i, cenario in enumerate(cenarios):
            dados_cenario = self.df[self.df['cenario'] == cenario]
            
            if not dados_cenario.empty:
                dados_seq = dados_cenario[dados_cenario['servidor'] == 'sequencial'].sort_values('num_clientes')
                dados_conc = dados_cenario[dados_cenario['servidor'] == 'concorrente'].sort_values('num_clientes')
                
                if not dados_seq.empty and not dados_conc.empty:
                    x = np.array(dados_seq['num_clientes'])
                    sucesso_seq = dados_seq['taxa_sucesso']
                    sucesso_conc = dados_conc['taxa_sucesso']
                    
                    axes[i].bar(x - 0.2, sucesso_seq, 0.4, label='Sequencial', color='lightcoral', alpha=0.8)
                    axes[i].bar(x + 0.2, sucesso_conc, 0.4, label='Concorrente', color='lightblue', alpha=0.8)
                    
                    axes[i].set_title(f'Cenário {cenarios_labels[i]}')
                    axes[i].set_xlabel('Número de Clientes')
                    axes[i].set_ylabel('Taxa de Sucesso (%)')
                    axes[i].set_ylim(0, 105)
                    axes[i].legend()
                    axes[i].grid(True, alpha=0.3)
                    axes[i].set_xticks(x)
                    
                    #Adicionar linha de referência em 100%
                    axes[i].axhline(y=100, color='green', linestyle='--', alpha=0.7)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/analise_taxa_sucesso.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfico de taxa de sucesso salvo: analise_taxa_sucesso.png")
    
    def grafico_analise_escalabilidade(self):
        #Gráfico de análise de escalabilidade
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle('Análise de Escalabilidade', fontsize=16, fontweight='bold')
        
        #Throughput vs Número de Clientes (cenário rápido)
        dados_rapido = self.df[self.df['cenario'] == 'rapido']
        
        if not dados_rapido.empty:
            dados_seq = dados_rapido[dados_rapido['servidor'] == 'sequencial'].sort_values('num_clientes')
            dados_conc = dados_rapido[dados_rapido['servidor'] == 'concorrente'].sort_values('num_clientes')
            
            if not dados_seq.empty and not dados_conc.empty:
                #Garantir que os dados tenham o mesmo tamanho
                clientes_seq = dados_seq['num_clientes'].values
                clientes_conc = dados_conc['num_clientes'].values
                
                #Usar apenas clientes que estão em ambos os datasets
                clientes_comuns = sorted(set(clientes_seq) & set(clientes_conc))
                
                if clientes_comuns:
                    #Filtrar dados para clientes comuns
                    dados_seq_filtrados = dados_seq[dados_seq['num_clientes'].isin(clientes_comuns)].sort_values('num_clientes')
                    dados_conc_filtrados = dados_conc[dados_conc['num_clientes'].isin(clientes_comuns)].sort_values('num_clientes')
                    
                    clientes = dados_seq_filtrados['num_clientes'].values
                    throughput_seq = dados_seq_filtrados['throughput'].values
                    throughput_conc = dados_conc_filtrados['throughput'].values
                    
                    ax1.plot(clientes, throughput_seq, 'o-', label='Sequencial', color='red', linewidth=2, markersize=8)
                    ax1.plot(clientes, throughput_conc, 's-', label='Concorrente', color='blue', linewidth=2, markersize=8)
                    ax1.set_title('Escalabilidade de Throughput (Cenário Rápido)')
                    ax1.set_xlabel('Número de Clientes')
                    ax1.set_ylabel('Throughput (req/s)')
                    ax1.legend()
                    ax1.grid(True, alpha=0.3)
                    
                    #Eficiência por Cliente
                    eficiencia_seq = throughput_seq / clientes
                    eficiencia_conc = throughput_conc / clientes
                    
                    ax2.plot(clientes, eficiencia_seq, 'o-', label='Sequencial', color='red', linewidth=2, markersize=8)
                    ax2.plot(clientes, eficiencia_conc, 's-', label='Concorrente', color='blue', linewidth=2, markersize=8)
                    ax2.set_title('Eficiência por Cliente')
                    ax2.set_xlabel('Número de Clientes')
                    ax2.set_ylabel('Eficiência (req/s por cliente)')
                    ax2.legend()
                    ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('resultados/graficos/analise_escalabilidade.png', dpi=300, bbox_inches='tight')
        plt.close()
        print("Gráfico de escalabilidade salvo: analise_escalabilidade.png")

    def gerar_relatorio(self):
        #Gera relatório de análise baseado no CSV
        if self.df is None or self.df.empty:
            print("Nenhum dado disponível para relatório")
            return
        
        relatorio = []
        relatorio.append("RELATÓRIO DE ANÁLISE DE PERFORMANCE")
        relatorio.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        relatorio.append(f"Registros analisados: {len(self.df)}")
        relatorio.append("")
        
        #Análise por cenário
        for cenario in ['rapido', 'medio', 'lento']:
            dados_cenario = self.df[self.df['cenario'] == cenario]
            if not dados_cenario.empty:
                relatorio.append(f"CENÁRIO {cenario.upper()}")
                
                for num_clientes in sorted(dados_cenario['num_clientes'].unique()):
                    dados_seq = dados_cenario[(dados_cenario['servidor'] == 'sequencial') & 
                                             (dados_cenario['num_clientes'] == num_clientes)]
                    dados_conc = dados_cenario[(dados_cenario['servidor'] == 'concorrente') & 
                                              (dados_cenario['num_clientes'] == num_clientes)]
                    
                    if not dados_seq.empty and not dados_conc.empty:
                        throughput_seq = dados_seq['throughput'].iloc[0]
                        throughput_conc = dados_conc['throughput'].iloc[0]
                        
                        relatorio.append(f"  {num_clientes} clientes:")
                        relatorio.append(f"    Sequencial: {throughput_seq:.2f} req/s")
                        relatorio.append(f"    Concorrente: {throughput_conc:.2f} req/s")
                        
                        if throughput_seq > 0:
                            melhoria = ((throughput_conc - throughput_seq) / throughput_seq) * 100
                            relatorio.append(f"    Melhoria: {melhoria:+.1f}%")
                
                relatorio.append("")
        
        #Salvar relatório
        os.makedirs('resultados', exist_ok=True)
        with open('resultados/relatorio_analise.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(relatorio))
        
        print("Relatório salvo em resultados/relatorio_analise.txt")

if __name__ == "__main__":
    analisador = AnalisadorResultados()
    analisador.gerar_todos_graficos()
    analisador.gerar_relatorio()
    
    print("\nGráficos gerados com sucesso!")
    print("Arquivos criados:")
    print("  - comparacao_throughput.png")
    print("  - comparacao_tempo_resposta.png")
    print("  - analise_taxa_sucesso.png")
    print("  - analise_escalabilidade.png")
    print("  - relatorio_analise.txt")
