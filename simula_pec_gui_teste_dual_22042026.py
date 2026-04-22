import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import colorsys
from scipy.stats import chi2
import pandas as pd
import time
import threading
from typing import List, Dict
from numba import jit, prange
from multiprocessing import Pool, cpu_count
import os
import plotly.graph_objects as go
from plotly.offline import plot as plotly_plot
from plotly.subplots import make_subplots


os.environ['NUMBA_NUM_THREADS'] = str(cpu_count())
rng = np.random.default_rng(seed=42)

TRANSLATIONS = {
    'pt': {
        'num_pcs_label': 'Número de PCs',
        'erro_pec_label': 'Erro admissível (PEC)',
        'perc_pcs_pec_label': '% PCs acima do PEC',
        'intervalo_acima_label': 'Intervalo acima (%)',
        'intervalo_abaixo_label': 'Intervalo abaixo (%)',
        'num_iteracoes_label': 'Nº de iterações',
        
        'progresso_label': 'Progresso:',
        'progresso_total_label': 'Progresso total:',
        
        'btn_carregar_dados': 'Carregar Dados Reais',
        'btn_confirmar': 'Confirmar',
        'btn_salvar_planilha': 'Salvar Planilha',
        'btn_salvar_grafico': 'Salvar Gráfico',
        'btn_salvar_grafico_dinamico': 'Salvar Gráfico Dinâmico',
        'btn_cancelar': 'Cancelar',
        'btn_original': 'Original',
        'btn_english': 'English',
        
        'msg_sucesso': 'Sucesso',
        'msg_erros_carregados': 'erros carregados.',
        'msg_erro': 'Erro',
        'msg_falha_leitura': 'Falha ao ler o arquivo: ',
        'msg_aviso': 'Aviso',
        'msg_executar_simulacao': 'Execute a simulação antes.',
        'msg_exportacao': 'Exportação',
        'msg_planilha_salva': 'Planilha salva com sucesso!',
        'msg_salvo': 'Salvo',
        'msg_grafico_salvo': 'Gráfico salvo com sucesso!',
        'msg_falha_grafico': 'Falha ao salvar o gráfico: ',
        'msg_cancelado': 'Cancelado',
        'msg_simulacao_interrompida': 'A simulação foi interrompida.',
        'msg_erro_inesperado': 'Ocorreu um erro inesperado: ',
        'msg_tempo_estimado': 'Tempo estimado',
        'msg_deseja_continuar': 'Deseja continuar?',
        
        'titulo_precisao': 'Curvas de Rejeição – Precisão',
        'titulo_norma': 'Curvas de Rejeição – Norma do país',
        'xlabel_amostra': 'Tamanho da Amostra',
        'ylabel_prm': 'PRM (%)',
        'legenda_dados_reais': 'R (Dados Reais)',
        'tempo_total': 'Tempo total: ',
        
        'sheet_title': 'Resultado SimulaPEC',
        'tamanho_amostra': 'Tamanho da amostra',
        'prm_precisao': 'PRM(%) - Precisão',
        'prm_norma': 'PRM(%) - Norma',
        'r10': 'R-10',
        
        'lang_title': 'Selecione o idioma / Select Language',
        'lang_instruction': 'Escolha o idioma desejado:',
    },
    'en': {
        'num_pcs_label': 'Number of PCs',
        'erro_pec_label': 'Acceptable error (PEC)',
        'perc_pcs_pec_label': '% PCs above PEC',
        'intervalo_acima_label': 'Interval above (%)',
        'intervalo_abaixo_label': 'Interval below (%)',
        'num_iteracoes_label': 'Nº of iterations',
        
        'progresso_label': 'Progress:',
        'progresso_total_label': 'Total progress:',
        
        'btn_carregar_dados': 'Load Real Data',
        'btn_confirmar': 'Confirm',
        'btn_salvar_planilha': 'Save Spreadsheet',
        'btn_salvar_grafico': 'Save Chart',
        'btn_salvar_grafico_dinamico': 'Save Dynamic Chart',
        'btn_cancelar': 'Cancel',
        'btn_original': 'Original',
        'btn_english': 'English',
        
        'msg_sucesso': 'Success',
        'msg_erros_carregados': 'errors loaded.',
        'msg_erro': 'Error',
        'msg_falha_leitura': 'Failed to read the file: ',
        'msg_aviso': 'Warning',
        'msg_executar_simulacao': 'Run the simulation before.',
        'msg_exportacao': 'Export',
        'msg_planilha_salva': 'Spreadsheet saved successfully!',
        'msg_salvo': 'Saved',
        'msg_grafico_salvo': 'Chart saved successfully!',
        'msg_falha_grafico': 'Failed to save chart: ',
        'msg_cancelado': 'Canceled',
        'msg_simulacao_interrompida': 'The simulation was interrupted.',
        'msg_erro_inesperado': 'An unexpected error occurred: ',
        'msg_tempo_estimado': 'Estimated time',
        'msg_deseja_continuar': 'Wanna continue?',
        
        'titulo_precisao': 'Rejection Curves – Accuracy',
        'titulo_norma': 'Rejection Curves – Country\'s Standard',
        'xlabel_amostra': 'Sample Size',
        'ylabel_prm': 'PRM (%)',
        'legenda_dados_reais': 'R (Real Data)',
        'tempo_total': 'Total time: ',
        
        'sheet_title': 'Results SimulaPEC',
        'tamanho_amostra': 'Sample Size',
        'prm_precisao': 'PRM(%) - Accuracy',
        'prm_norma': 'PRM(%) - Country\'s Standard',
        'r10': 'R-10',
        
        'lang_title': 'Select Language',
        'lang_instruction': 'Choose your preferred language:',
    }
}


@jit(nopython=True, cache=True)
def gerar_tabela_base(n_pontos, erro_maximo, percentual_acima):
    np.random.seed(0)
    erros = np.zeros(n_pontos, dtype=np.float64)
    
    for i in range(n_pontos):
        u1 = np.random.random()
        u2 = np.random.random()
        erros[i] = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
    
    erros_abs = np.abs(erros)
    erros_ordenados = np.sort(erros_abs)[::-1]
    
    index_limite = int(n_pontos * percentual_acima / 100)
    valor_limite = erros_ordenados[index_limite - 1]
    k = erro_maximo / valor_limite
    
    return erros * k

@jit(nopython=True, parallel=True, cache=True)
def _simular_batch_numba(base, n, n_iter, erro_padrao_precisao,
                         erro_admissivel, percentual_limite, qui_tabela,
                         indices_pool=None):
    rejeicoes_p = 0
    rejeicoes_n = 0
    n_base = len(base)
    
    use_pool = indices_pool is not None
    
    for i in prange(n_iter):
        amostra = np.empty(n, dtype=np.float64)
        
        if use_pool and len(indices_pool) >= n:
            for j in range(n):
                amostra[j] = base[indices_pool[j]]
        else:
            for j in range(n):
                idx = np.random.randint(0, n_base)
                amostra[j] = base[idx]
        
        media = np.sum(amostra) / n
        desvio_sq = np.sum((amostra - media) ** 2) / (n - 1)
        
        qui_calc = ((n - 1) * desvio_sq) / (erro_padrao_precisao ** 2)
        if qui_calc > qui_tabela:
            rejeicoes_p += 1
        
        acima = np.sum(np.abs(amostra) > erro_admissivel)
        porcentagem_acima = (acima / n) * 100
        if porcentagem_acima > percentual_limite:
            rejeicoes_n += 1
    
    return rejeicoes_p, rejeicoes_n


def simular_percentual_rejeicao_escalar(
    base, tamanhos, n_iter, erro_admissivel, percentual_limite,
    progress_callback=None, tempo_estimado=False, batch_size=100, indices_pool=None):
    
    resultado_precisao = []
    resultado_norma = []
    
    start = time.time()
    erro_padrao_precisao = erro_admissivel / 1.6449
    
    qui_tabelas = {n: chi2.ppf(1 - (percentual_limite / 100), df=n - 1) 
                   for n in tamanhos}
    
    if tempo_estimado:
        n = tamanhos[0]
        qui_tabela = qui_tabelas[n]
        tempo_estimado_val = _simular_batch_numba(
            base, n, batch_size, erro_padrao_precisao,
            erro_admissivel, percentual_limite, qui_tabela, indices_pool)
        tempo_batch = time.time() - start
        tempo_total_estimado = tempo_batch * (n_iter / batch_size) * len(tamanhos)
        return tempo_total_estimado
    
    for idx, n in enumerate(tamanhos):
        if progress_callback:
            progress_callback(idx + 1, len(tamanhos))
        
        qui_tabela = qui_tabelas[n]
        
        num_batches = (n_iter + batch_size - 1) // batch_size
        rejeicoes_p_total = 0
        rejeicoes_n_total = 0
        
        for batch_idx in range(num_batches):
            current_batch = min(batch_size, n_iter - (batch_idx * batch_size))
            
            rejeicoes_p, rejeicoes_n = _simular_batch_numba(
                base, n, current_batch, erro_padrao_precisao,
                erro_admissivel, percentual_limite, qui_tabela, indices_pool)
            
            rejeicoes_p_total += rejeicoes_p
            rejeicoes_n_total += rejeicoes_n
        
        resultado_precisao.append((rejeicoes_p_total / n_iter) * 100)
        resultado_norma.append((rejeicoes_n_total / n_iter) * 100)
    
    return resultado_precisao, resultado_norma

def _salvar_planilha_csv(
    caminho_arquivo: str,
    percentuais: list[float],
    amostras: list[int],
    prm_precisao_list: List[Dict[int, float]],
    prm_norma_list: List[Dict[int, float]],
    dados_reais: bool = False,
    prm_precisao_real: dict[int, float] | None = None,
    prm_norma_real: dict[int, float] | None = None,
    lang: str = 'pt'
) -> None:
    
    if lang == 'en':
        header_sample = "Sample Size"
        header_precision = "PRM(%) - Accuracy"
        header_standard = "PRM(%) - Country's Standard"
        header_real_section = "R-10"
    else:
        header_sample = "Tamanho da amostra"
        header_precision = "PRM(%) - Precisão"
        header_standard = "PRM(%) - Norma"
        header_real_section = "R-10"
    
    with open(caminho_arquivo, 'w', encoding='utf-8', newline='') as f:
        for p in percentuais:
            f.write(f"\n=== {p}% ===\n")
            f.write(f"{header_sample},{header_precision},{header_standard}\n")
        
        for n in amostras:
            row_values = [str(n)]
            for i, _perc in enumerate(percentuais):
                dic_prec = prm_precisao_list[i]
                dic_norm = prm_norma_list[i]
                row_values.append(f"{dic_prec.get(n, 0.0):.2f}")
                row_values.append(f"{dic_norm.get(n, 0.0):.2f}")
            f.write(",".join(row_values) + "\n")
        
        if dados_reais and prm_precisao_real is not None and prm_norma_real is not None:
            f.write(f"\n=== {header_real_section} ===\n")
            f.write(f"{header_sample},{header_precision},{header_standard}\n")
            for n in amostras:
                prec_val = prm_precisao_real.get(n, 0.0)
                norm_val = prm_norma_real.get(n, 0.0)
                f.write(f"{n},{prec_val:.2f},{norm_val:.2f}\n")

def _calcular_estimativa_tempo(base, tamanhos_amostra, n_iter, erro_admissivel, 
                               perc_base, batch_size, indices_pool):
    if not tamanhos_amostra:
        return 0
    
    pontos_teste = []
    if len(tamanhos_amostra) >= 2:
        pontos_teste = [tamanhos_amostra[0], tamanhos_amostra[len(tamanhos_amostra)//2]]
    else:
        pontos_teste = [tamanhos_amostra[0]]
    
    iter_estimativa = 10    
    tempos_medidos = []
    
    for n_teste in pontos_teste:
        qui_tabela = chi2.ppf(1 - (perc_base / 100), df=n_teste - 1)
        start = time.time()
        rejeicoes_p, rejeicoes_n = _simular_batch_numba(
            base, n_teste, iter_estimativa, 
            erro_admissivel / 1.6449, 
            erro_admissivel, perc_base, qui_tabela, indices_pool)
        tempo_gasto = time.time() - start
        
        tempos_medidos.append((n_teste, tempo_gasto / iter_estimativa))
    
    if len(tempos_medidos) < 2:
        n_ref, t_ref = tempos_medidos[0]
        fator_crescimento = (tamanhos_amostra[-1] / n_ref)
        tempo_medio_por_iter = t_ref * fator_crescimento
    else:
        n1, t1 = tempos_medidos[0]
        n2, t2 = tempos_medidos[1]
        
        if n2 == n1:
            a = 0
            b = t1
        else:
            a = (t2 - t1) / (n2 - n1)
            b = t1 - a * n1
        
        n_medio = sum(tamanhos_amostra) / len(tamanhos_amostra)
        tempo_medio_por_iter = max(a * n_medio + b, 0.001)

    total_itens = len(tamanhos_amostra)
    tempo_ciclo = tempo_medio_por_iter * n_iter * total_itens
    
    return tempo_ciclo

def _formatar_tempo(segundos):
    if segundos < 60:
        return f"{segundos:.2f} s"
    
    horas = int(segundos // 3600)
    minutos = int((segundos % 3600) // 60)
    seg_rest = segundos % 60
    
    partes = []
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    partes.append(f"{seg_rest:.2f}s")
    
    return " ".join(partes)

DEFAULT_LINEWIDTH = 2.5
def _line_width():
    return DEFAULT_LINEWIDTH


class SimulaPECApp:
    def __init__(self, master, lang='pt'):
        self.master = master
        self.lang = lang
        self.t = TRANSLATIONS[lang]
        
        master.title(f"SimulaPEC {'Teste' if lang == 'pt' else 'Test'} 22/04/2026")

        self.dados_reais = None
        self.curvas_precisao = []
        self.curvas_norma = []
        self.curvas_precisao: List[List[float]] = []
        self.curvas_norma: List[List[float]] = []
        self.percentuais = []
        self.tamanhos_amostra = []
        self.curva_precisao_R = None
        self.curva_norma_R = None
        self.figura = None
        self.entries = {}
        self.perc_max = None
        self.intervalo = None
        self.amostras = []
        self.prm_precisao = {}
        self.prm_norma = {}
        self.dados_reais = False
        self.prm_precisao_real = {}
        self.prm_norma_real = {}
        self.prm_precisao_real: Dict[int, float] = {}
        self.prm_norma_real: Dict[int, float] = {}
        self.prm_precisao_list: List[Dict[int, float]] = []
        self.prm_norma_list: List[Dict[int, float]] = []

        self._cancel_requested = False
        self._thread_worker = None

        campos = [
            (self.t['num_pcs_label'], "150"),
            (self.t['erro_pec_label'], "5"),
            (self.t['perc_pcs_pec_label'], "10"),
            (self.t['intervalo_acima_label'], "5"),
            (self.t['intervalo_abaixo_label'], "2"),
            (self.t['num_iteracoes_label'], "3000")]

        for i, (label, default) in enumerate(campos):
            tk.Label(master, text=label).grid(row=i+2, column=0, sticky="e")
            entry = tk.Entry(master)
            entry.insert(0, default)
            entry.grid(row=i+2, column=1)
            self.entries[label] = entry

        self.label_progresso = tk.Label(master, text=f"{self.t['progresso_label']} 0%")
        self.label_progresso.grid(row=9, column=0, columnspan=2)

        self.progress = ttk.Progressbar(master, length=200, mode='determinate')
        self.progress.grid(row=10, column=0, columnspan=2, pady=5)

        self.label_total = tk.Label(master, text=f"{self.t['progresso_total_label']} 0%")
        self.label_total.grid(row=11, column=0, columnspan=2)

        self.progress_total = ttk.Progressbar(master, length=200,
                                              mode='determinate')
        self.progress_total.grid(row=12, column=0, columnspan=2, pady=5)

        tk.Button(master, text=self.t['btn_carregar_dados'],
                  command=self.carregar_dados_reais).grid(row=13, column=0)
        tk.Button(master, text=self.t['btn_confirmar'],
                  command=self.executar).grid(row=13, column=1)
        tk.Button(master, text=self.t['btn_salvar_planilha'],
                  command=self.exportar_planilha).grid(row=14, column=0)
        tk.Button(master, text=self.t['btn_salvar_grafico'],
                  command=self.exportar_grafico).grid(row=14, column=1)
        
        tk.Button(master, text=self.t['btn_salvar_grafico_dinamico'],
                  command=self.exportar_grafico_html).grid(row=15, column=0, columnspan=2, pady=5)

        self.btn_cancelar = tk.Button(master, text=self.t['btn_cancelar'],
                                      command=self.cancelar, state="disabled")
        self.btn_cancelar.grid(row=16, column=0, columnspan=2, pady=5)

    def disable_ui_during_run(self):
        self.progress_total['value'] = 0
        self.label_total.config(text=f"{self.t['progresso_total_label']} 0%")
        for child in self.master.winfo_children():
            if isinstance(child, tk.Button) and child["text"] != self.t['btn_cancelar']:
                child.configure(state="disabled")
        self.btn_cancelar.configure(state="normal")
        self.progress['value'] = 0
        self.label_progresso.config(text=f"{self.t['progresso_label']} 0%")

    def enable_ui_after_run(self):
        for child in self.master.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(state="normal")

        self.btn_cancelar.configure(state="disabled")
        self.progress_total['value'] = 100
        self.label_total.config(text=f"{self.t['progresso_total_label']} 100%")

    def cancelar(self):
        self._cancel_requested = True
        self.btn_cancelar.configure(state="disabled")

    def atualizar_progresso(self, valor, total):
        pct = int((valor / total) * 100)
        self.progress['value'] = pct
        self.label_progresso.config(text=f"{self.t['progresso_label']} {pct}%")
        self.master.update_idletasks()

    def atualizar_progresso_total(self, concluido, total):
        pct = int((concluido / total) * 100)
        self.progress_total['value'] = pct
        self.label_total.config(text=f"{self.t['progresso_total_label']} {pct}%")
        self.master.update_idletasks()

    def _gerar_cores_personalizadas(self, percentuais, perc_base):
        cores = []

        dist_max = max(
            abs(p - perc_base) for p in percentuais if p != perc_base
            ) if len([p for p in percentuais if p != perc_base]) > 0 else 1
        
        for perc in percentuais:
            if perc == perc_base:
                cores.append('#1f77b4')
            elif perc < perc_base:
                distancia = abs(perc - perc_base) / dist_max
                r, g, b = colorsys.hls_to_rgb(0.33, 0.9 - (0.6 * distancia), 0.5)
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(r * 255), int(g * 255), int(b * 255))
                cores.append(hex_color)
            else:
                distancia = abs(perc - perc_base) / dist_max
                r, g, b = colorsys.hls_to_rgb(0.0, 0.9 - (0.6 * distancia), 0.5)
                hex_color = '#{:02x}{:02x}{:02x}'.format(
                    int(r * 255), int(g * 255), int(b * 255))
                cores.append(hex_color)

        return cores

    def carregar_dados_reais(self):
        caminho = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if caminho:
            try:
                with open(caminho, "r") as f:
                    linhas = f.readlines()
                    self.dados_reais = [
                        float(l.strip().replace(",", "."))
                        for l in linhas if l.strip()
                    ]
                messagebox.showinfo(self.t['msg_sucesso'],
                                    f"{len(self.dados_reais)} {self.t['msg_erros_carregados']}")
            except Exception as e:
                messagebox.showerror(self.t['msg_erro'], 
                                     f"{self.t['msg_falha_leitura']}{e}")

    def executar(self):
        self._cancel_requested = False
        self.disable_ui_during_run()
        self._thread_worker = threading.Thread(target=self._processar_simulacao)
        self._thread_worker.start()

    def _ask_continue(self, tempo_formatado):
        self._continue_resp = None

        def _callback():
            msg_tempo = tempo_formatado if isinstance(tempo_formatado, str) else _formatar_tempo(tempo_formatado)
            resp = messagebox.askyesno(
                self.t['msg_tempo_estimado'],
                f"Tempo estimado: {msg_tempo}\n{self.t['msg_deseja_continuar']}")
            self._continue_resp = resp

        self.master.after(0, _callback)

        while self._continue_resp is None:
            self.master.update()
            time.sleep(0.05)
        return self._continue_resp

    def _finalizar_thread(self, cancelado: bool):
        def _restore():
            self.enable_ui_after_run()
            if cancelado:
                messagebox.showinfo(self.t['msg_cancelado'], 
                                    self.t['msg_simulacao_interrompida'])
        self.master.after(0, _restore)

    def _processar_simulacao(self):
        try:
            N = int(self.entries[self.t['num_pcs_label']].get())
            erro_admissivel = float(self.entries[self.t['erro_pec_label']].get())
            self.erro_admissivel = erro_admissivel
            perc_base = float(self.entries[self.t['perc_pcs_pec_label']].get())
            self.perc_base = perc_base
            intervalo_acima = float(self.entries[self.t['intervalo_acima_label']].get())
            intervalo_abaixo = float(self.entries[self.t['intervalo_abaixo_label']].get())
            n_iter = int(self.entries[self.t['num_iteracoes_label']].get())

            if N <= 0 or erro_admissivel <= 0 or perc_base <= 0 or \
                intervalo_acima <= 0 or intervalo_abaixo <= 0 or n_iter <= 0:
                raise ValueError()

            self.tamanhos_amostra = list(range(5, int(N * 0.6) + 1, 5))
            self.percentuais = []

            perc = perc_base - intervalo_abaixo
            while perc > 0:
                self.percentuais.append(perc)
                perc -= intervalo_abaixo
            self.percentuais.append(perc_base)
            perc = perc_base + intervalo_acima
            while perc <= 40:
                self.percentuais.append(perc)
                perc += intervalo_acima
            self.percentuais.sort()

            max_tamanho = max(self.tamanhos_amostra)
            indices_pool = None

            if N > 100000:
                indices_pool = rng.choice(N, size=max_tamanho, replace=False)
            else:
                indices_pool = None
            
            base_teste = gerar_tabela_base(N, erro_admissivel, perc_base)
            if N > 200000:
                batch_size = 50
            elif N > 100000:
                batch_size = 100
            else:
                batch_size = 200
            
            tempo_ciclo_estimado = _calcular_estimativa_tempo(
                base_teste, self.tamanhos_amostra,
                n_iter, erro_admissivel,
                perc_base, batch_size, indices_pool)
            tempo_total_segundos = tempo_ciclo_estimado
            tempo_formatado = _formatar_tempo(tempo_total_segundos)

            if not self._ask_continue(tempo_formatado):
                self._finalizar_thread(cancelado=True)
                return
            
            self.inicio_processamento = time.time()
            self.curvas_precisao.clear()
            self.curvas_norma.clear()
            self.prm_precisao_list.clear()
            self.prm_norma_list.clear()
            self.prm_precisao_real.clear()
            self.prm_norma_real.clear()

            for idx, perc in enumerate(self.percentuais):
                if self._cancel_requested:
                    self._finalizar_thread(cancelado=True)
                    return
                
                base = gerar_tabela_base(N, erro_admissivel, perc)
                if N > 100000:
                    base = base.astype(np.float32)
                pr_p, pr_n = simular_percentual_rejeicao_escalar(
                    base, self.tamanhos_amostra, n_iter,
                    erro_admissivel, perc,
                    progress_callback=self.atualizar_progresso,
                    batch_size=batch_size,
                    indices_pool=indices_pool)
                self.curvas_precisao.append(pr_p)
                self.curvas_norma.append(pr_n)

                dic_prec = {n: round(v, 2) for n, v in zip(self.tamanhos_amostra, pr_p)}
                dic_norm = {n: round(v, 2) for n, v in zip(self.tamanhos_amostra, pr_n)}
                self.prm_precisao_list.append(dic_prec)
                self.prm_norma_list.append(dic_norm)
                self.atualizar_progresso_total(concluido=idx + 1, total=len(self.percentuais))
            
            if self.dados_reais:
                base_real = np.array(self.dados_reais)
                if len(base_real) > 100000:
                    base_real = base_real.astype(np.float32)
                pr_p_r, pr_n_r = simular_percentual_rejeicao_escalar(
                    base_real, self.tamanhos_amostra, n_iter,
                    erro_admissivel, perc_base,
                    progress_callback=self.atualizar_progresso,
                    batch_size=batch_size)
                self.curva_precisao_R = pr_p_r
                self.curva_norma_R = pr_n_r

                self.prm_precisao_real = {n: round(v, 2) for n, v in zip(self.tamanhos_amostra, pr_p_r)}
                self.prm_norma_real = {n: round(v, 2) for n, v in zip(self.tamanhos_amostra, pr_n_r)}
                self.atualizar_progresso_total(concluido=len(self.percentuais) + 1,total=len(self.percentuais) + 1)
            
            self.tempo_processamento = time.time() - self.inicio_processamento
            self.master.after(0, self.plotar)
            self._finalizar_thread(cancelado=False)
        
        except Exception as exc:
            self.master.after(0, lambda: messagebox.showerror(
                self.t['msg_erro'], f"{self.t['msg_erro_inesperado']}{exc}"))
            self._finalizar_thread(cancelado=True)

    def plotar(self):
        fig, ax = plt.subplots(1, 2, figsize=(14, 6))
        perc_base = self.perc_base
        n_curvas = len(self.percentuais)
        cores = self._gerar_cores_personalizadas(self.percentuais, perc_base)

        secs = self.tempo_processamento
        tempo_formatado = _formatar_tempo(secs)

        pec_valor = getattr(self, 'erro_admissivel', 0)
        titulo_precisao = f"{self.t['titulo_precisao']} (PEC: {pec_valor})"
        titulo_norma = f"{self.t['titulo_norma']} (PEC: {pec_valor})"

        for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_precisao)):
            ax[0].plot(self.tamanhos_amostra, curva,
                       label=f"{perc}%", color=cores[i], linewidth=_line_width())

        if self.curva_precisao_R is not None:
            ax[0].plot(self.tamanhos_amostra, self.curva_precisao_R,
                       label=self.t['legenda_dados_reais'], 
                       linewidth=_line_width() * 1.5,
                       color='black', linestyle='--')

        ax[0].set_title(titulo_precisao)
        ax[0].set_xlabel(self.t['xlabel_amostra'])
        ax[0].set_ylabel(self.t['ylabel_prm'])
        ax[0].legend()
        ax[0].grid(True)

        for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_norma)):
            ax[1].plot(self.tamanhos_amostra, curva,
                       label=f"{perc}%", color=cores[i], linewidth=_line_width())

        if self.curva_norma_R is not None:
            ax[1].plot(self.tamanhos_amostra, self.curva_norma_R,
                       label=self.t['legenda_dados_reais'], 
                       linewidth=_line_width() * 1.5,
                       color='black', linestyle='--')

        ax[1].set_title(titulo_norma)
        ax[1].set_xlabel(self.t['xlabel_amostra'])
        ax[1].set_ylabel(self.t['ylabel_prm'])
        ax[1].legend()
        ax[1].grid(True)

        plt.tight_layout()
        ax[0].xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax[1].xaxis.set_major_locator(ticker.MaxNLocator(integer=True))

        fig.text(0.58, 0.98,
                 f"{self.t['tempo_total']}{tempo_formatado}",
                 ha='right', va='top',
                 fontsize=10,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

        plt.show(block=False)
        self.figura = fig

    def exportar_grafico_html(self):
        if not self.figura:
            messagebox.showwarning(self.t['msg_aviso'],
                                   self.t['msg_executar_simulacao'])
            return
        
        caminho = filedialog.asksaveasfilename(
            defaultextension=".html",
            filetypes=[("HTML files", "*.html")])
        if not caminho:
            return
        
        try:
            fig = go.Figure()
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=(
                    f"{self.t['titulo_precisao']} (PEC: {self.erro_admissivel})",
                    f"{self.t['titulo_norma']} (PEC: {self.erro_admissivel})"),
                    horizontal_spacing=0.1)
            
            perc_base = self.perc_base
            cores = self._gerar_cores_personalizadas(self.percentuais, perc_base)

            for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_precisao)):
                fig.add_trace(go.Scatter(
                    x=self.tamanhos_amostra,
                    y=curva,
                    mode='lines',
                    name=f"{perc}%",
                    line=dict(color=cores[i], width=2.5)), row=1, col=1)
            if self.curva_precisao_R is not None:
                fig.add_trace(go.Scatter(
                    x=self.tamanhos_amostra,
                    y=self.curva_precisao_R,
                    mode='lines',
                    name=self.t['legenda_dados_reais'],
                    line=dict(color='black', width=3, dash='dash')), row=1, col=1)
            
            for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_norma)):
                fig.add_trace(go.Scatter(
                    x=self.tamanhos_amostra,
                    y=curva,
                    mode='lines',
                    name=f"{perc}%",
                    line=dict(color=cores[i], width=2.5)), row=1, col=2)
            if self.curva_norma_R is not None:
                fig.add_trace(go.Scatter(
                    x=self.tamanhos_amostra,
                    y=self.curva_norma_R,
                    mode='lines',
                    name=self.t['legenda_dados_reais'],
                    line=dict(color='black', width=3, dash='dash')), row=1, col=2)
            
            fig.update_xaxes(title_text=self.t['xlabel_amostra'], row=1, col=1)
            fig.update_yaxes(title_text=self.t['ylabel_prm'], row=1, col=1)
            fig.update_xaxes(title_text=self.t['xlabel_amostra'], row=1, col=2)
            fig.update_yaxes(title_text=self.t['ylabel_prm'], row=1, col=2)

            fig.update_layout(
                hovermode='x unified',
                showlegend=True,
                legend=dict(orientation='v', yanchor='middle', y=1, xanchor='left', x=1.02),
                template='plotly_white',
                width=1200,
                height=600,
                title_text="")
            
            fig.write_html(caminho, include_plotlyjs='cdn', full_html=True)
            messagebox.showinfo(self.t['msg_salvo'], self.t['msg_grafico_salvo'])

        except Exception as exc:
            messagebox.showerror(self.t['msg_erro'],
                                 f"{self.t['msg_falha_grafico']}{exc}")
    
    def exportar_planilha(self):
        if not self.curvas_precisao:
            messagebox.showwarning(self.t['msg_aviso'],
                                   self.t['msg_executar_simulacao'])
            return
        
        caminho = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")])
        if not caminho:
            return
        
        amostras = self.tamanhos_amostra
        _salvar_planilha_csv(
            caminho_arquivo=caminho,
            percentuais=self.percentuais,
            amostras=amostras,
            prm_precisao_list=self.prm_precisao_list,
            prm_norma_list=self.prm_norma_list,
            dados_reais=self.dados_reais,
            prm_precisao_real=self.prm_precisao_real,
            prm_norma_real=self.prm_norma_real,
            lang=self.lang)
        
        messagebox.showinfo(self.t['msg_exportacao'], self.t['msg_planilha_salva'])

    def exportar_grafico(self):
        if not self.figura:
            messagebox.showwarning(self.t['msg_aviso'], self.t['msg_executar_simulacao'])
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png")]
        )
        if not caminho:
            return

        try:
            self.figura.savefig(caminho, dpi=300, bbox_inches="tight")
            messagebox.showinfo(self.t['msg_salvo'], self.t['msg_grafico_salvo'])
        except Exception as exc:
            messagebox.showerror(self.t['msg_erro'], f"{self.t['msg_falha_grafico']}{exc}")


class LanguageSelector:
    def __init__(self, root):
        self.root = root
        self.root.title("SimulaPEC - Selecione o idioma / Select Language")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        self.selected_lang = None
        
        self.root.update_idletasks()
        width = 400
        height = 200
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        frame = tk.Frame(root, padx=20, pady=20)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Escolha o idioma / Choose language:", 
                 font=('Arial', 12, 'bold'), pady=10).pack()
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Original", width=20, height=2,
                  bg="#e1f5fe", command=lambda: self.select_lang('pt')).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="English", width=20, height=2,
                  bg="#e1f5fe", command=lambda: self.select_lang('en')).pack(side=tk.LEFT, padx=10)
    
    def select_lang(self, lang):
        self.selected_lang = lang
        self.root.withdraw()
        self.root.event_generate("<<LangSelected>>", when="tail")


def main():
    root = tk.Tk()
    selector = LanguageSelector(root)
    app_instance = [None] 
    
    def on_lang_selected(event):
        if selector.selected_lang:
            selector.root.destroy()
            
            new_root = tk.Tk()
            new_root.title(f"SimulaPEC {'Teste' if selector.selected_lang == 'pt' else 'Test'} 22/04/2026")
            
            app_instance[0] = SimulaPECApp(new_root, lang=selector.selected_lang)
            
            new_root.mainloop()
    
    root.bind("<<LangSelected>>", on_lang_selected)
    
    root.mainloop()

if __name__ == "__main__":
    main()