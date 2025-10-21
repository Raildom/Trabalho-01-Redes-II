#!/usr/bin/env python3

#Teste Completo do Projeto Redes II
#Arquivo único para testar servidores sequencial e concorrente
#Consolida funcionalidades de teste_cliente.py e testes_automatizados.py

import sys
import os
import csv
import time
import argparse
import threading
import statistics
from datetime import datetime

#Adicionar diretório src ao path (um nível acima da pasta testes)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from cliente import ClienteHTTP
    from configuracao import ID_CUSTOMIZADO, PORTA_SERVIDOR
except ImportError as e:
    print(f"[ERRO] Erro ao importar módulos: {e}")
    print("Certifique-se de estar no diretório correto do projeto")
    sys.exit(1)

# ============================================================================
# CONFIGURACOES DE TESTE - ALTERE AQUI CONFORME NECESSARIO
# ============================================================================

# Quantidades de clientes simultaneos para testar (altere aqui)
clientes_teste = [1, 5]

# Numero de requisicoes por cliente em cada teste (altere aqui)  
requisicoes_por_cliente = 2

# Configuracoes para teste de concorrencia simples
concorrencia_clientes = 5
concorrencia_requisicoes = 3

# ============================================================================

class TestadorCarga:
    #Classe para executar testes de carga e concorrencia
    def __init__(self, host_servidor, porta_servidor=PORTA_SERVIDOR):
        self.cliente = ClienteHTTP(host_servidor, porta_servidor)
        self.resultados = []
        self.lock = threading.Lock()
        
    def teste_requisicao_unica(self, metodo='GET', caminho='/', id_cliente=None):
        #Executa um único teste de requisição
        resultado = self.cliente.enviar_requisicao(metodo, caminho)
        resultado['id_cliente'] = id_cliente
        resultado['timestamp'] = time.time()
        
        with self.lock:
            self.resultados.append(resultado)
        
        return resultado
    
    def teste_concorrente(self, num_clientes, requisicoes_por_cliente, metodo='GET', caminho='/'):
        #Executa teste com múltiplos clientes simultâneos
        threads = []
        self.resultados = []
        
        print(f"Iniciando teste com {num_clientes} clientes, {requisicoes_por_cliente} requisições cada")
        
        tempo_inicio = time.time()
        
        def executar_cliente(id_cliente):
            for i in range(requisicoes_por_cliente):
                self.teste_requisicao_unica(metodo, caminho, f"{id_cliente}-{i}")
                time.sleep(0.01)  #Pequeno delay entre requisições
        
        #Criar e iniciar threads
        for i in range(num_clientes):
            thread = threading.Thread(target=executar_cliente, args=(i,))
            threads.append(thread)
            thread.start()

        #Aguardar conclusão de todas as threads
        for thread in threads:
            thread.join()
        
        tempo_total = time.time() - tempo_inicio
        
        return {
            'tempo_total': tempo_total,
            'num_clientes': num_clientes,
            'requisicoes_por_cliente': requisicoes_por_cliente,
            'total_requisicoes': len(self.resultados),
            'resultados': self.resultados
        }
    
    def gerar_relatorio(self, resultado_teste):
        #Gera relatório detalhado do teste
        resultados = resultado_teste['resultados']
        sucessos = [r for r in resultados if r['sucesso']]
        falhas = [r for r in resultados if not r['sucesso']]
        
        if sucessos:
            tempos_resposta = [r['tempo_resposta'] for r in sucessos]
            tempo_medio = statistics.mean(tempos_resposta)
            tempo_min = min(tempos_resposta)
            tempo_max = max(tempos_resposta)
            tempo_mediano = statistics.median(tempos_resposta)
            desvio_padrao = statistics.stdev(tempos_resposta) if len(tempos_resposta) > 1 else 0
        else:
            tempo_medio = tempo_min = tempo_max = tempo_mediano = desvio_padrao = 0
        
        throughput = len(sucessos) / resultado_teste['tempo_total'] if resultado_teste['tempo_total'] > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"               RELATÓRIO DETALHADO DE TESTE")
        print(f"{'='*60}")
        
        # Estatísticas gerais
        print(f"\n[ESTATÍSTICAS GERAIS]")
        print(f"  Total de requisições enviadas: {len(resultados)}")
        print(f"  Requisições bem-sucedidas:     {len(sucessos)}")
        print(f"  Requisições com falha:         {len(falhas)}")
        print(f"  Taxa de sucesso:               {(len(sucessos)/len(resultados)*100):.1f}%")
        print(f"  Clientes simultâneos:          {resultado_teste['num_clientes']}")
        print(f"  Requisições por cliente:       {resultado_teste['requisicoes_por_cliente']}")
        
        # Métricas de tempo
        print(f"\n[MÉTRICAS DE DESEMPENHO]")
        print(f"  Tempo total de execução:       {resultado_teste['tempo_total']:.2f} segundos")
        print(f"  Throughput (requisições/seg):  {throughput:.2f} req/s")
        
        if sucessos:
            print(f"\n[ANÁLISE DE TEMPO DE RESPOSTA]")
            print(f"  Tempo médio de resposta:       {tempo_medio*1000:.1f} ms")
            print(f"  Tempo mínimo de resposta:      {tempo_min*1000:.1f} ms")
            print(f"  Tempo máximo de resposta:      {tempo_max*1000:.1f} ms")
            print(f"  Tempo mediano de resposta:     {tempo_mediano*1000:.1f} ms")
            print(f"  Desvio padrão:                 {desvio_padrao*1000:.1f} ms")
            
            # Percentis
            tempos_ordenados = sorted(tempos_resposta)
            p95 = tempos_ordenados[int(0.95 * len(tempos_ordenados))]
            p99 = tempos_ordenados[int(0.99 * len(tempos_ordenados))]
            print(f"  Percentil 95%:                 {p95*1000:.1f} ms")
            print(f"  Percentil 99%:                 {p99*1000:.1f} ms")
        
        # Análise de qualidade
        if falhas:
            print(f"\n[ANÁLISE DE FALHAS]")
            tipos_erro = {}
            for falha in falhas:
                erro = falha.get('erro', 'Erro desconhecido')
                tipos_erro[erro] = tipos_erro.get(erro, 0) + 1
            
            for erro, count in tipos_erro.items():
                print(f"  {erro}: {count} ocorrências")
        
        # Avaliação da qualidade do serviço
        print(f"\n[AVALIAÇÃO DE QUALIDADE]")
        if len(sucessos) == len(resultados):
            print(f"  Status: EXCELENTE - Todas as requisições foram atendidas")
        elif len(sucessos) >= len(resultados) * 0.95:
            print(f"  Status: MUITO BOM - {(len(sucessos)/len(resultados)*100):.1f}% de sucesso")
        elif len(sucessos) >= len(resultados) * 0.90:
            print(f"  Status: BOM - {(len(sucessos)/len(resultados)*100):.1f}% de sucesso")
        elif len(sucessos) >= len(resultados) * 0.75:
            print(f"  Status: REGULAR - {(len(sucessos)/len(resultados)*100):.1f}% de sucesso")
        else:
            print(f"  Status: RUIM - Apenas {(len(sucessos)/len(resultados)*100):.1f}% de sucesso")
        
        if sucessos and tempo_medio < 0.100:
            print(f"  Responsividade: EXCELENTE - Tempo médio < 100ms")
        elif sucessos and tempo_medio < 0.500:
            print(f"  Responsividade: BOA - Tempo médio < 500ms")
        elif sucessos and tempo_medio < 1.000:
            print(f"  Responsividade: REGULAR - Tempo médio < 1s")
        elif sucessos:
            print(f"  Responsividade: LENTA - Tempo médio > 1s")
        
        print(f"{'='*60}")

class TestadorAutomatizado:
    #Classe para executar testes automatizados
    def __init__(self):
        self.resultados = {}
        
    def executar_todos_testes(self):
        #Executa todos os testes automatizados
        print("=== Iniciando Testes Automatizados ===")
        print(f"Data/Hora: {datetime.now()}")
        
        #Endereços dos servidores (baseado no docker-compose)
        servidores = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        
        #Diferentes cenários de teste
        cenarios_teste = [
            {'nome': 'rapido', 'caminho': '/rapido', 'descricao': 'Processamento rápido'},
            {'nome': 'medio', 'caminho': '/medio', 'descricao': 'Processamento médio (0.5s)'},
            {'nome': 'lento', 'caminho': '/lento', 'descricao': 'Processamento lento (2s)'},
        ]
        
        #Configurações de teste (usando valores das configurações do topo)
        # Para alterar: modifique as variáveis no topo do arquivo
        
        for tipo_servidor, ip_servidor in servidores.items():
            print(f"\n=== Testando Servidor {tipo_servidor.upper()} ({ip_servidor}) ===")
            self.resultados[tipo_servidor] = {}
            
            for cenario in cenarios_teste:
                print(f"\n--- Cenário: {cenario['descricao']} ---")
                self.resultados[tipo_servidor][cenario['nome']] = {}
                
                for num_clientes in clientes_teste:
                    print(f"\nTestando com {num_clientes} clientes simultâneos...")
                    
                    testador = TestadorCarga(ip_servidor)
                    resultado = testador.teste_concorrente(
                        num_clientes, 
                        requisicoes_por_cliente,
                        'GET',
                        cenario['caminho']
                    )
                    
                    self.resultados[tipo_servidor][cenario['nome']][num_clientes] = resultado
                    testador.gerar_relatorio(resultado)
        
        self.salvar_resultados()
        self.gerar_comparacao()
    
    def salvar_resultados(self):
        #Salva os resultados finais em arquivo TXT e CSV
        os.makedirs('/app/resultados', exist_ok=True)
        
        # Primeiro gerar o arquivo CSV
        self.gerar_csv()
        
        nome_arquivo = '/app/resultados/resultados dos testes.txt'
        
        with open(nome_arquivo, 'w', encoding='ascii', errors='ignore') as f:
            f.write(f"ID Personalizado: {ID_CUSTOMIZADO}\n")
            
            # Resumo detalhado por servidor
            for tipo_servidor in ['sequencial', 'concorrente']:
                if tipo_servidor in self.resultados:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"SERVIDOR {tipo_servidor.upper()}\n")
                    f.write(f"{'='*80}\n")
                    
                    # Estatísticas gerais do servidor
                    total_requisicoes = 0
                    total_sucessos = 0
                    tempos_servidor = []
                    
                    for cenario in ['rapido', 'medio', 'lento']:
                        if cenario in self.resultados[tipo_servidor]:
                            descricoes = {
                                'rapido': 'Processamento Instantaneo',
                                'medio': 'Processamento 0.5 segundos',
                                'lento': 'Processamento 2.0 segundos'
                            }
                            
                            f.write(f"\n[{cenario.upper()} - {descricoes[cenario]}]\n")
                            f.write(f"{'-'*60}\n")
                            
                            for num_clientes in clientes_teste:
                                if num_clientes in self.resultados[tipo_servidor][cenario]:
                                    resultado = self.resultados[tipo_servidor][cenario][num_clientes]
                                    
                                    sucessos = len([r for r in resultado['resultados'] if r['sucesso']])
                                    total = len(resultado['resultados'])
                                    falhas = total - sucessos
                                    taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
                                    throughput = sucessos / resultado['tempo_total'] if resultado['tempo_total'] > 0 else 0
                                    
                                    # Acumular estatísticas gerais
                                    total_requisicoes += total
                                    total_sucessos += sucessos
                                    
                                    if sucessos > 0:
                                        tempos = [r['tempo_resposta'] for r in resultado['resultados'] if r['sucesso']]
                                        tempo_medio = sum(tempos) / len(tempos) * 1000  # em ms
                                        tempo_min = min(tempos) * 1000
                                        tempo_max = max(tempos) * 1000
                                        tempos_servidor.extend(tempos)
                                    else:
                                        tempo_medio = tempo_min = tempo_max = 0
                                    
                                    # Linha principal com métricas
                                    f.write(f"  {num_clientes:2d} clientes simultaneos:\n")
                                    f.write(f"    - Requisicoes enviadas: {total}\n")
                                    f.write(f"    - Sucessos: {sucessos} | Falhas: {falhas} | Taxa: {taxa_sucesso:5.1f}%\n")
                                    f.write(f"    - Throughput: {throughput:6.2f} req/s\n")
                                    f.write(f"    - Tempo medio de resposta: {tempo_medio:6.1f}ms\n")
                                    f.write(f"    - Tempo de execucao total: {resultado['tempo_total']:.2f} segundos\n")
                                    
                                    if sucessos > 0:
                                        f.write(f"    - Detalhes de tempo: Min {tempo_min:5.1f}ms | Max {tempo_max:6.1f}ms\n")
                                        
                                        # Avaliacao qualitativa
                                        if throughput >= 50:
                                            avaliacao = "EXCELENTE"
                                        elif throughput >= 20:
                                            avaliacao = "MUITO BOM"
                                        elif throughput >= 10:
                                            avaliacao = "BOM"
                                        elif throughput >= 5:
                                            avaliacao = "REGULAR"
                                        else:
                                            avaliacao = "BAIXO"
                                        
                                        f.write(f"    - Avaliacao de desempenho: {avaliacao}\n")
                                    else:
                                        f.write(f"    - ERRO: Todas as requisicoes falharam\n")
                                    
                                    f.write(f"\n")
                    
                    # Resumo geral do servidor
                    if total_requisicoes > 0:
                        taxa_geral = (total_sucessos / total_requisicoes * 100)
                        f.write(f"{'-'*60}\n")
                        f.write(f"RESUMO GERAL DO SERVIDOR {tipo_servidor.upper()}:\n")
                        f.write(f"  - Total de requisicoes processadas: {total_requisicoes}\n")
                        f.write(f"  - Taxa de sucesso geral: {taxa_geral:.1f}%\n")
                        
                        if tempos_servidor:
                            tempo_medio_geral = sum(tempos_servidor) / len(tempos_servidor) * 1000
                            f.write(f"  - Tempo medio geral: {tempo_medio_geral:.1f}ms\n")
                            
                            # Classificacao geral
                            if taxa_geral >= 99:
                                classificacao = "EXCELENTE - Sistema muito confiavel"
                            elif taxa_geral >= 95:
                                classificacao = "MUITO BOM - Sistema confiavel"
                            elif taxa_geral >= 90:
                                classificacao = "BOM - Sistema estavel"
                            elif taxa_geral >= 80:
                                classificacao = "REGULAR - Necessita melhorias"
                            else:
                                classificacao = "CRITICO - Sistema instavel"
                            
                            f.write(f"  - Classificacao: {classificacao}\n")
            
            # Comparacao detalhada entre servidores
            f.write(f"\n{'='*80}\n")
            f.write("                  COMPARACAO DETALHADA ENTRE SERVIDORES\n")
            f.write(f"{'='*80}\n")
            
            if 'sequencial' in self.resultados and 'concorrente' in self.resultados:
                # Cabecalho da tabela de comparacao
                f.write(f"\nFormato: [Cenario] Clientes -> Sequencial vs Concorrente (Diferenca)\n")
                f.write(f"{'-'*80}\n")
                
                for cenario in ['rapido', 'medio', 'lento']:
                    if (cenario in self.resultados['sequencial'] and 
                        cenario in self.resultados['concorrente']):
                        
                        descricoes = {
                            'rapido': 'Processamento Instantaneo',
                            'medio': 'Processamento 0.5s',
                            'lento': 'Processamento 2.0s'
                        }
                        
                        f.write(f"\n[{cenario.upper()} - {descricoes[cenario]}]\n")
                        
                        melhorias_cenario = []
                        
                        for num_clientes in clientes_teste:
                            if (num_clientes in self.resultados['sequencial'][cenario] and 
                                num_clientes in self.resultados['concorrente'][cenario]):
                                
                                seq = self.resultados['sequencial'][cenario][num_clientes]
                                conc = self.resultados['concorrente'][cenario][num_clientes]
                                
                                seq_sucessos = len([r for r in seq['resultados'] if r['sucesso']])
                                conc_sucessos = len([r for r in conc['resultados'] if r['sucesso']])
                                
                                seq_throughput = seq_sucessos / seq['tempo_total'] if seq['tempo_total'] > 0 else 0
                                conc_throughput = conc_sucessos / conc['tempo_total'] if conc['tempo_total'] > 0 else 0
                                
                                # Calcular tempos médios
                                if seq_sucessos > 0:
                                    seq_tempos = [r['tempo_resposta'] for r in seq['resultados'] if r['sucesso']]
                                    seq_tempo_medio = sum(seq_tempos) / len(seq_tempos) * 1000
                                else:
                                    seq_tempo_medio = 0
                                    
                                if conc_sucessos > 0:
                                    conc_tempos = [r['tempo_resposta'] for r in conc['resultados'] if r['sucesso']]
                                    conc_tempo_medio = sum(conc_tempos) / len(conc_tempos) * 1000
                                else:
                                    conc_tempo_medio = 0
                                
                                f.write(f"  {num_clientes:2d} clientes simultaneos:\n")
                                f.write(f"    + Sequencial:  {seq_throughput:6.2f} req/s | Tempo medio: {seq_tempo_medio:6.1f}ms\n")
                                f.write(f"    + Concorrente: {conc_throughput:6.2f} req/s | Tempo medio: {conc_tempo_medio:6.1f}ms\n")
                                
                                if seq_throughput > 0 and conc_throughput > 0:
                                    melhoria_throughput = ((conc_throughput - seq_throughput) / seq_throughput) * 100
                                    melhoria_tempo = ((seq_tempo_medio - conc_tempo_medio) / seq_tempo_medio) * 100 if seq_tempo_medio > 0 else 0
                                    
                                    melhorias_cenario.append(melhoria_throughput)
                                    
                                    f.write(f"    > Throughput: ")
                                    if melhoria_throughput > 20:
                                        f.write(f"CONCORRENTE MUITO MELHOR (+{melhoria_throughput:5.1f}%)\n")
                                    elif melhoria_throughput > 5:
                                        f.write(f"CONCORRENTE MELHOR (+{melhoria_throughput:5.1f}%)\n")
                                    elif melhoria_throughput > -5:
                                        f.write(f"EMPATE TECNICO ({melhoria_throughput:+5.1f}%)\n")
                                    elif melhoria_throughput > -20:
                                        f.write(f"SEQUENCIAL MELHOR ({melhoria_throughput:5.1f}%)\n")
                                    else:
                                        f.write(f"SEQUENCIAL MUITO MELHOR ({melhoria_throughput:5.1f}%)\n")
                                    
                                    f.write(f"    > Tempo resposta: ")
                                    if melhoria_tempo > 20:
                                        f.write(f"CONCORRENTE MUITO MAIS RAPIDO (-{abs(melhoria_tempo):5.1f}%)\n")
                                    elif melhoria_tempo > 5:
                                        f.write(f"CONCORRENTE MAIS RAPIDO (-{abs(melhoria_tempo):5.1f}%)\n")
                                    elif melhoria_tempo > -5:
                                        f.write(f"TEMPOS SIMILARES ({melhoria_tempo:+5.1f}%)\n")
                                    elif melhoria_tempo > -20:
                                        f.write(f"SEQUENCIAL MAIS RAPIDO (+{abs(melhoria_tempo):5.1f}%)\n")
                                    else:
                                        f.write(f"SEQUENCIAL MUITO MAIS RAPIDO (+{abs(melhoria_tempo):5.1f}%)\n")
                                else:
                                    f.write(f"    > ERRO: Nao foi possivel comparar (falhas nas requisicoes)\n")
                                
                                f.write(f"\n")
                        
                        # Resumo do cenario
                        if melhorias_cenario:
                            melhoria_media = sum(melhorias_cenario) / len(melhorias_cenario)
                            f.write(f"  Resumo do cenario {cenario.upper()}:\n")
                            if melhoria_media > 30:
                                f.write(f"    * CONCORRENTE MUITO SUPERIOR (media +{melhoria_media:.1f}%)\n")
                            elif melhoria_media > 15:
                                f.write(f"    * CONCORRENTE SUPERIOR (media +{melhoria_media:.1f}%)\n")
                            elif melhoria_media > 5:
                                f.write(f"    * CONCORRENTE LIGEIRAMENTE MELHOR (media +{melhoria_media:.1f}%)\n")
                            elif melhoria_media > -5:
                                f.write(f"    = DESEMPENHO SIMILAR (media {melhoria_media:+.1f}%)\n")
                            else:
                                f.write(f"    - SEQUENCIAL MELHOR (media {melhoria_media:+.1f}%)\n")
                        f.write(f"\n")
            

        
        print(f"\n[SUCESSO] Resultados finais salvos em {nome_arquivo}")
    
    def gerar_csv(self):
        """Gera arquivo CSV com todos os resultados dos testes"""
        import csv
        
        nome_arquivo_csv = '/app/resultados/resultados_completos.csv'
        
        try:
            with open(nome_arquivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'servidor', 'cenario', 'num_clientes', 'requisicoes_enviadas', 
                    'sucessos', 'falhas', 'taxa_sucesso', 'throughput', 
                    'tempo_total', 'tempo_medio_ms', 'tempo_min_ms', 'tempo_max_ms'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                # Processar dados de cada servidor
                for tipo_servidor in ['sequencial', 'concorrente']:
                    if tipo_servidor in self.resultados:
                        for cenario in ['rapido', 'medio', 'lento']:
                            if cenario in self.resultados[tipo_servidor]:
                                for num_clientes in clientes_teste:
                                    if num_clientes in self.resultados[tipo_servidor][cenario]:
                                        resultado = self.resultados[tipo_servidor][cenario][num_clientes]
                                        
                                        # Calcular métricas
                                        sucessos = len([r for r in resultado['resultados'] if r['sucesso']])
                                        total = len(resultado['resultados'])
                                        falhas = total - sucessos
                                        taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
                                        throughput = sucessos / resultado['tempo_total'] if resultado['tempo_total'] > 0 else 0
                                        
                                        if sucessos > 0:
                                            tempos = [r['tempo_resposta'] for r in resultado['resultados'] if r['sucesso']]
                                            tempo_medio = sum(tempos) / len(tempos) * 1000  # em ms
                                            tempo_min = min(tempos) * 1000
                                            tempo_max = max(tempos) * 1000
                                        else:
                                            tempo_medio = tempo_min = tempo_max = 0
                                        
                                        # Escrever linha no CSV
                                        writer.writerow({
                                            'servidor': tipo_servidor,
                                            'cenario': cenario,
                                            'num_clientes': num_clientes,
                                            'requisicoes_enviadas': total,
                                            'sucessos': sucessos,
                                            'falhas': falhas,
                                            'taxa_sucesso': round(taxa_sucesso, 1),
                                            'throughput': round(throughput, 2),
                                            'tempo_total': round(resultado['tempo_total'], 2),
                                            'tempo_medio_ms': round(tempo_medio, 1),
                                            'tempo_min_ms': round(tempo_min, 1),
                                            'tempo_max_ms': round(tempo_max, 1)
                                        })
            
            print(f"[SUCESSO] Arquivo CSV gerado: {nome_arquivo_csv}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao gerar CSV: {e}")
    
    def gerar_comparacao(self):
        #Gera comparação entre servidores
        print("\n=== COMPARAÇÃO ENTRE SERVIDORES ===")
        
        if 'sequencial' in self.resultados and 'concorrente' in self.resultados:
            for cenario in ['rapido', 'medio', 'lento']:
                if cenario in self.resultados['sequencial'] and cenario in self.resultados['concorrente']:
                    print(f"\n--- Cenário: {cenario} ---")
                    
                    for num_clientes in clientes_teste:
                        if (num_clientes in self.resultados['sequencial'][cenario] and 
                            num_clientes in self.resultados['concorrente'][cenario]):
                            
                            seq = self.resultados['sequencial'][cenario][num_clientes]
                            conc = self.resultados['concorrente'][cenario][num_clientes]
                            
                            seq_sucessos = len([r for r in seq['resultados'] if r['sucesso']])
                            conc_sucessos = len([r for r in conc['resultados'] if r['sucesso']])
                            
                            seq_throughput = seq_sucessos / seq['tempo_total'] if seq['tempo_total'] > 0 else 0
                            conc_throughput = conc_sucessos / conc['tempo_total'] if conc['tempo_total'] > 0 else 0
                            
                            print(f"  {num_clientes} clientes:")
                            print(f"    Sequencial: {seq_throughput:.2f} req/s")
                            print(f"    Concorrente: {conc_throughput:.2f} req/s")
                            
                            if seq_throughput > 0:
                                melhoria = ((conc_throughput - seq_throughput) / seq_throughput) * 100
                                print(f"    Melhoria: {melhoria:.1f}%")

class TestadorProjeto:
    #Classe principal para testes do projeto
    
    def __init__(self):
        self.servidores_docker = {
            'sequencial': '76.1.0.10',
            'concorrente': '76.1.0.11'
        }
        self.servidores_local = {
            'sequencial': 'localhost:8080',
            'concorrente': 'localhost:8081'
        }
    
    def detectar_ambiente(self):
        #Detecta qual ambiente está disponível
        #Tenta Docker primeiro
        try:
            cliente = ClienteHTTP(self.servidores_docker['sequencial'])
            resultado = cliente.enviar_requisicao('GET', '/')
            if resultado['sucesso']:
                return 'docker'
        except:
            pass
        
        #Tenta local
        try:
            cliente = ClienteHTTP('localhost', 8080)
            resultado = cliente.enviar_requisicao('GET', '/')
            if resultado['sucesso']:
                return 'local'
        except:
            pass
        
        return None
    
    def teste_conectividade_basica(self, ambiente='docker'):
        #Executa teste básico de conectividade
        print("\n" + "="*70)
        print("                    TESTE DE CONECTIVIDADE")
        print("="*70)
        
        if ambiente == 'docker':
            configuracao_rede = "76.01.0.0/16"
            ip_servidor = "76.01.0.10"
            print(f"\n[CONFIGURAÇÃO DE REDE]")
            print(f"  Ambiente:           Docker Containers")
            print(f"  Subnet configurada: {configuracao_rede}")
            print(f"  IP base servidor:   {ip_servidor}")
            print(f"  ID Personalizado:   {ID_CUSTOMIZADO}")
        else:
            print(f"\n[CONFIGURAÇÃO DE REDE]")
            print(f"  Ambiente:           Local (Host)")
            print(f"  ID Personalizado:   {ID_CUSTOMIZADO}")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        resultados_conectividade = {}
        
        print(f"\n[TESTANDO SERVIDORES]")
        for tipo_servidor, endereco in servidores.items():
            print(f"\n  Servidor {tipo_servidor.upper()} ({endereco})")
            print(f"  {'-'*50}")
            
            try:
                if ':' in endereco:
                    host, porta = endereco.split(':')
                    cliente = ClienteHTTP(host, int(porta))
                else:
                    cliente = ClienteHTTP(endereco)
                
                # Executa múltiplas requisições para teste mais robusto
                testes = []
                for i in range(3):
                    resultado = cliente.enviar_requisicao('GET', '/')
                    testes.append(resultado)
                
                sucessos = [t for t in testes if t['sucesso']]
                resultados_conectividade[tipo_servidor] = {
                    'total': len(testes),
                    'sucessos': len(sucessos),
                    'falhas': len(testes) - len(sucessos)
                }
                
                if sucessos:
                    tempo_medio = sum(t['tempo_resposta'] for t in sucessos) / len(sucessos)
                    tempo_min = min(t['tempo_resposta'] for t in sucessos)
                    tempo_max = max(t['tempo_resposta'] for t in sucessos)
                    
                    print(f"  Status:               [CONECTADO]")
                    print(f"  Código HTTP:          {sucessos[0]['codigo_status']}")
                    print(f"  Taxa de sucesso:      {len(sucessos)}/{len(testes)} ({len(sucessos)/len(testes)*100:.0f}%)")
                    print(f"  Tempo médio:          {tempo_medio*1000:.1f} ms")
                    print(f"  Tempo mínimo:         {tempo_min*1000:.1f} ms")
                    print(f"  Tempo máximo:         {tempo_max*1000:.1f} ms")
                    
                    # Verificar cabeçalhos
                    cabecalhos = sucessos[0].get('cabecalhos', {})
                    if 'X-Custom-ID' in cabecalhos:
                        print(f"  X-Custom-ID:          [PRESENTE] {cabecalhos['X-Custom-ID'][:16]}...")
                    else:
                        print(f"  X-Custom-ID:          [AUSENTE]")
                        
                    # Avaliação de desempenho
                    if tempo_medio < 0.050:
                        print(f"  Avaliação:            EXCELENTE (< 50ms)")
                    elif tempo_medio < 0.100:
                        print(f"  Avaliação:            MUITO BOM (< 100ms)")
                    elif tempo_medio < 0.200:
                        print(f"  Avaliação:            BOM (< 200ms)")
                    else:
                        print(f"  Avaliação:            LENTO (> 200ms)")
                        
                else:
                    print(f"  Status:               [DESCONECTADO]")
                    print(f"  Erro:                 {testes[0].get('erro', 'Erro desconhecido')}")
                    
            except Exception as e:
                print(f"  Status:               [ERRO CRÍTICO]")
                print(f"  Exceção:              {str(e)}")
                resultados_conectividade[tipo_servidor] = {
                    'total': 0,
                    'sucessos': 0,
                    'falhas': 1
                }
        
        # Resumo final
        print(f"\n{'='*70}")
        print(f"                      RESUMO DE CONECTIVIDADE")
        print(f"{'='*70}")
        
        total_servidores = len(servidores)
        servidores_online = sum(1 for r in resultados_conectividade.values() if r['sucessos'] > 0)
        
        print(f"\n[RESUMO GERAL]")
        print(f"  Servidores testados:      {total_servidores}")
        print(f"  Servidores online:        {servidores_online}")
        print(f"  Servidores offline:       {total_servidores - servidores_online}")
        print(f"  Taxa de disponibilidade:  {servidores_online/total_servidores*100:.0f}%")
        
        if servidores_online == total_servidores:
            print(f"  Status geral:             [TODOS OPERACIONAIS]")
        elif servidores_online > 0:
            print(f"  Status geral:             [PARCIALMENTE OPERACIONAL]")
        else:
            print(f"  Status geral:             [SISTEMA INDISPONÍVEL]")
        
        print(f"\n  Para executar todos os testes, use:")
        print(f"  python teste_completo.py --completo")
        print(f"{'='*70}")
    
    def teste_endpoints(self, ambiente='docker'):
        #Testa diferentes endpoints dos servidores
        print("\n" + "="*70)
        print("                    TESTE DE ENDPOINTS")
        print("="*70)
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        endpoints_config = [
            {'path': '/', 'nome': 'Raiz', 'descricao': 'Endpoint padrão'},
            {'path': '/rapido', 'nome': 'Rápido', 'descricao': 'Processamento instantâneo'},
            {'path': '/medio', 'nome': 'Médio', 'descricao': 'Processamento 0.5s'},
            {'path': '/lento', 'nome': 'Lento', 'descricao': 'Processamento 2s'}
        ]
        
        resultados_endpoints = {}
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n[SERVIDOR {tipo_servidor.upper()}] ({endereco})")
            print(f"  {'-'*60}")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
                cliente = ClienteHTTP(host, int(porta))
            else:
                cliente = ClienteHTTP(endereco)
            
            resultados_servidor = {}
            
            for endpoint_config in endpoints_config:
                endpoint = endpoint_config['path']
                nome = endpoint_config['nome']
                descricao = endpoint_config['descricao']
                
                try:
                    resultado = cliente.enviar_requisicao('GET', endpoint)
                    
                    if resultado['sucesso']:
                        tempo_ms = resultado['tempo_resposta'] * 1000
                        status_icon = "[✓]" if resultado['codigo_status'] == 200 else "[!]"
                        
                        print(f"  {nome:8} {endpoint:8} {status_icon} HTTP {resultado['codigo_status']} - {tempo_ms:6.1f} ms - {descricao}")
                        
                        resultados_servidor[endpoint] = {
                            'sucesso': True,
                            'tempo': resultado['tempo_resposta'],
                            'status': resultado['codigo_status']
                        }
                    else:
                        print(f"  {nome:8} {endpoint:8} [✗] ERRO     - {resultado.get('erro', 'Falha na requisição')}")
                        resultados_servidor[endpoint] = {
                            'sucesso': False,
                            'erro': resultado.get('erro', 'Erro desconhecido')
                        }
                        
                except Exception as e:
                    print(f"  {nome:8} {endpoint:8} [✗] EXCEÇÃO - {str(e)}")
                    resultados_servidor[endpoint] = {
                        'sucesso': False,
                        'erro': str(e)
                    }
            
            resultados_endpoints[tipo_servidor] = resultados_servidor
            
            # Estatísticas do servidor
            sucessos = sum(1 for r in resultados_servidor.values() if r.get('sucesso', False))
            total = len(resultados_servidor)
            print(f"  {'-'*60}")
            print(f"  Endpoints funcionais: {sucessos}/{total} ({sucessos/total*100:.0f}%)")
            
            if sucessos > 0:
                tempos = [r['tempo'] for r in resultados_servidor.values() if r.get('sucesso', False)]
                tempo_medio = sum(tempos) / len(tempos)
                print(f"  Tempo médio:         {tempo_medio*1000:.1f} ms")
        
        # Resumo comparativo
        print(f"\n{'='*70}")
        print(f"                     RESUMO DE ENDPOINTS")
        print(f"{'='*70}")
        
        for endpoint_config in endpoints_config:
            endpoint = endpoint_config['path']
            nome = endpoint_config['nome']
            
            print(f"\n[{nome.upper()} - {endpoint}]")
            
            for tipo_servidor in servidores.keys():
                if tipo_servidor in resultados_endpoints and endpoint in resultados_endpoints[tipo_servidor]:
                    resultado = resultados_endpoints[tipo_servidor][endpoint]
                    if resultado.get('sucesso', False):
                        tempo_ms = resultado['tempo'] * 1000
                        print(f"  {tipo_servidor:12}: [OK] {tempo_ms:6.1f} ms (HTTP {resultado['status']})")
                    else:
                        print(f"  {tipo_servidor:12}: [ERRO] {resultado.get('erro', 'Falha')}")
                else:
                    print(f"  {tipo_servidor:12}: [N/A] Não testado")
        
        print(f"{'='*70}")
    
    def teste_validacao_cabecalho(self, ambiente='docker'):
        #Valida se o cabeçalho X-Custom-ID está presente
        print("\n=== Teste de Validação de Cabeçalho ===")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n--- Servidor {tipo_servidor} ---")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
                cliente = ClienteHTTP(host, int(porta))
            else:
                cliente = ClienteHTTP(endereco)
            
            resultado = cliente.enviar_requisicao('GET', '/')
            
            if resultado['sucesso']:
                cabecalhos = resultado.get('cabecalhos', {})
                if 'X-Custom-ID' in cabecalhos:
                    print(f"  [SUCESSO] X-Custom-ID encontrado: {cabecalhos['X-Custom-ID']}")
                    if cabecalhos['X-Custom-ID'] == ID_CUSTOMIZADO:
                        print(f"  [SUCESSO] ID correto!")
                    else:
                        print(f"  [AVISO] ID diferente do esperado")
                else:
                    print(f"  [ERRO] X-Custom-ID não encontrado nos cabeçalhos")
            else:
                print(f"  [ERRO] Falha na requisição")
    
    def teste_concorrencia(self, ambiente='docker'):
        #Executa teste de concorrência básico
        print("\n=== Teste de Concorrência ===")
        
        servidores = self.servidores_docker if ambiente == 'docker' else self.servidores_local
        resultados = {}
        
        for tipo_servidor, endereco in servidores.items():
            print(f"\n--- Servidor {tipo_servidor} ---")
            
            if ':' in endereco:
                host, porta = endereco.split(':')
            else:
                host, porta = endereco, PORTA_SERVIDOR
            
            testador = TestadorCarga(host, int(porta))
            resultado = testador.teste_concorrente(concorrencia_clientes, concorrencia_requisicoes, 'GET', '/medio')
            testador.gerar_relatorio(resultado)
            resultados[tipo_servidor] = resultado
        
        return resultados
    
    def executar_tudo(self, ambiente=None):
        #Executa todos os testes disponíveis
        if ambiente is None:
            ambiente = self.detectar_ambiente()
            if ambiente is None:
                print("[ERRO] Nenhum servidor disponível")
                return
        
        print(f"=== Executando todos os testes (ambiente: {ambiente}) ===")
        
        self.teste_conectividade_basica(ambiente)
        self.teste_endpoints(ambiente)
        self.teste_validacao_cabecalho(ambiente)
        resultados_concorrencia = self.teste_concorrencia(ambiente)
        
        #Gerar CSV com os resultados dos testes de concorrência
        self.gerar_csv_basico(resultados_concorrencia)
        
        print("\n" + "="*60)
        
        return True

    #Gera arquivo CSV com os resultados dos testes básicos de concorrência
    def gerar_csv_basico(self, resultados_concorrencia):
        
        #Criar diretório se não existir
        os.makedirs('resultados', exist_ok=True)
        nome_arquivo_csv = 'resultados/resultados_completos.csv'
        
        try:
            with open(nome_arquivo_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'servidor', 'cenario', 'num_clientes', 'requisicoes_enviadas', 
                    'sucessos', 'falhas', 'taxa_sucesso', 'throughput', 
                    'tempo_total', 'tempo_medio_ms', 'tempo_min_ms', 'tempo_max_ms'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                #Processar dados de cada servidor
                for tipo_servidor, resultado in resultados_concorrencia.items():
                    #Calcular métricas
                    sucessos = len([r for r in resultado['resultados'] if r['sucesso']])
                    total = len(resultado['resultados'])
                    falhas = total - sucessos
                    taxa_sucesso = (sucessos / total * 100) if total > 0 else 0
                    throughput = sucessos / resultado['tempo_total'] if resultado['tempo_total'] > 0 else 0
                    
                    if sucessos > 0:
                        tempos = [r['tempo_resposta'] for r in resultado['resultados'] if r['sucesso']]
                        tempo_medio = sum(tempos) / len(tempos) * 1000  #em ms
                        tempo_min = min(tempos) * 1000
                        tempo_max = max(tempos) * 1000
                    else:
                        tempo_medio = tempo_min = tempo_max = 0
                    
                    #Escrever linha no CSV
                    writer.writerow({
                        'servidor': tipo_servidor,
                        'cenario': 'medio',
                        'num_clientes': concorrencia_clientes,
                        'requisicoes_enviadas': total,
                        'sucessos': sucessos,
                        'falhas': falhas,
                        'taxa_sucesso': round(taxa_sucesso, 1),
                        'throughput': round(throughput, 2),
                        'tempo_total': round(resultado['tempo_total'], 2),
                        'tempo_medio_ms': round(tempo_medio, 1),
                        'tempo_min_ms': round(tempo_min, 1),
                        'tempo_max_ms': round(tempo_max, 1)
                    })
            
            print(f"\n[SUCESSO] Arquivo CSV gerado: {nome_arquivo_csv}")
            
        except Exception as e:
            print(f"[ERRO] Falha ao gerar CSV: {e}")

def main():
    #Função principal
    parser = argparse.ArgumentParser(description='Testador Completo do Projeto Redes II')
    parser.add_argument('--ambiente', choices=['docker', 'local'], 
                       help='Especificar ambiente (docker ou local)')
    parser.add_argument('--conectividade', action='store_true',
                       help='Executar apenas teste de conectividade')
    parser.add_argument('--endpoints', action='store_true',
                       help='Executar apenas teste de endpoints')
    parser.add_argument('--cabecalho', action='store_true',
                       help='Executar apenas teste de validação de cabeçalho')
    parser.add_argument('--concorrencia', action='store_true',
                       help='Executar apenas teste de concorrência')
    parser.add_argument('--completo', action='store_true',
                       help='Executar testes automatizados completos')
    
    args = parser.parse_args()
    
    if args.completo:
        #Executar testes automatizados completos
        testador_auto = TestadorAutomatizado()
        testador_auto.executar_todos_testes()
    else:
        #Executar testes básicos
        testador = TestadorProjeto()
        
        #Se nenhum teste específico foi especificado, executar tudo
        if not any([args.conectividade, args.endpoints, args.cabecalho, args.concorrencia]):
            testador.executar_tudo(args.ambiente)
        else:
            #Detectar ambiente se não especificado
            ambiente = args.ambiente
            if ambiente is None:
                ambiente = testador.detectar_ambiente()
                if ambiente is None:
                    print("[ERRO] Nenhum servidor disponível")
                    return

            #Executar testes específicos
            if args.conectividade:
                testador.teste_conectividade_basica(ambiente)
            
            if args.endpoints:
                testador.teste_endpoints(ambiente)
            
            if args.cabecalho:
                testador.teste_validacao_cabecalho(ambiente)
            
            if args.concorrencia:
                testador.teste_concorrencia(ambiente)

if __name__ == "__main__":
    main()
