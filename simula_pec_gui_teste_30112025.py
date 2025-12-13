import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import colorsys                     
from scipy.stats import chi2
import pandas as pd
import time
import threading

def gerar_tabela_base(n_pontos, erro_maximo, percentual_acima):
    np.random.seed(0)
    erros = np.random.normal(loc=0, scale=1, size=n_pontos)
    erros_abs = np.abs(erros)
    erros_ordenados = np.sort(erros_abs)[::-1]

    index_limite = int(n_pontos * percentual_acima / 100)
    valor_limite = erros_ordenados[index_limite - 1]
    k = erro_maximo / valor_limite
    return erros * k


def teste_precisao(amostra, erro_padrao_aceitavel):
    n = len(amostra)
    desvio_padrao = np.std(amostra, ddof=1)
    qui_calc = ((n - 1) * (desvio_padrao ** 2)) / (erro_padrao_aceitavel ** 2)
    qui_tabela = chi2.ppf(1 - 0.10, df=n - 1)
    return qui_calc <= qui_tabela


def teste_norma_brasileira(amostra, erro_admissivel, percentual_limite):
    acima = np.sum(np.abs(amostra) > erro_admissivel)
    porcentagem_acima = (acima / len(amostra)) * 100
    return porcentagem_acima <= percentual_limite


def simular_percentual_rejeicao(
    base, tamanhos, n_iter, erro_admissivel, percentual_limite,
    progress_callback=None, tempo_estimado=False
):
    resultado_precisao = []
    resultado_norma = []
    start = time.time()

    for idx, n in enumerate(tamanhos):
        rejeicoes_p = rejeicoes_n = 0

        for _ in range(n_iter):
            amostra = np.random.choice(base, size=n, replace=True)

            if not teste_precisao(amostra, erro_admissivel * 0.6):
                rejeicoes_p += 1

            if not teste_norma_brasileira(amostra, erro_admissivel, percentual_limite):
                rejeicoes_n += 1

        resultado_precisao.append((rejeicoes_p / n_iter) * 100)
        resultado_norma.append((rejeicoes_n / n_iter) * 100)

        if progress_callback:
            progress_callback(idx + 1, len(tamanhos))

        if tempo_estimado:
            break

    if tempo_estimado:
        return time.time() - start

    return resultado_precisao, resultado_norma

DEFAULT_LINEWIDTH = 2.5
def _line_width():
    return DEFAULT_LINEWIDTH

class SimulaPECApp:
    def __init__(self, master):
        self.master = master
        master.title("Simula PEC 2025 30/11/2025")

        self.dados_reais = None
        self.curvas_precisao = []
        self.curvas_norma = []
        self.percentuais = []
        self.tamanhos_amostra = []
        self.curva_precisao_R = None
        self.curva_norma_R = None
        self.figura = None
        self.entries = {}

        self._cancel_requested = False
        self._thread_worker = None

        campos = [
            ("Número de PCs", "600"),
            ("Erro admissível (PEC)", "5"),
            ("% PCs acima do PEC", "10"),
            ("Intervalo acima (%)", "24"),
            ("Intervalo abaixo (%)", "2"),
            ("Nº de iterações", "300")
        ]

        for i, (label, default) in enumerate(campos):
            tk.Label(master, text=label).grid(row=i, column=0, sticky="e")
            entry = tk.Entry(master)
            entry.insert(0, default)
            entry.grid(row=i, column=1)
            self.entries[label] = entry

        self.label_progresso = tk.Label(master, text="Progresso: 0%")
        self.label_progresso.grid(row=7, column=0, columnspan=2)

        self.progress = ttk.Progressbar(master, length=200, mode='determinate')
        self.progress.grid(row=8, column=0, columnspan=2, pady=5)

        tk.Button(master, text="Carregar Dados Reais",
                  command=self.carregar_dados_reais).grid(row=9, column=0)
        tk.Button(master, text="Confirmar",
                  command=self.executar).grid(row=9, column=1)
        tk.Button(master, text="Salvar Planilha",
                  command=self.exportar_planilha).grid(row=10, column=0)
        tk.Button(master, text="Salvar Gráfico",
                  command=self.exportar_grafico).grid(row=10, column=1)

        self.btn_cancelar = tk.Button(master, text="Cancelar",
                                      command=self.cancelar, state="disabled")
        self.btn_cancelar.grid(row=11, column=0, columnspan=2, pady=5)

    def disable_ui_during_run(self):
        for child in self.master.winfo_children():
            if isinstance(child, tk.Button) and child["text"] != "Cancelar":
                child.configure(state="disabled")
        self.btn_cancelar.configure(state="normal")
        self.progress['value'] = 0
        self.label_progresso.config(text="Progresso: 0%")

    def enable_ui_after_run(self):
        for child in self.master.winfo_children():
            if isinstance(child, tk.Button):
                child.configure(state="normal")
        self.btn_cancelar.configure(state="disabled")

    def cancelar(self):
        """Marca a flag de cancelamento; a thread de trabalho vai encerrar logo depois."""
        self._cancel_requested = True
        self.btn_cancelar.configure(state="disabled")

    def atualizar_progresso(self, valor, total):
        pct = int((valor / total) * 100)
        self.progress['value'] = pct
        self.label_progresso.config(text=f"Progresso: {pct}%")
        self.master.update_idletasks()

    def _gerar_cores(self, n):
        """Retorna `n` cores distintas a partir de um colormap, levemente escurecidas."""
        cmap = plt.get_cmap('tab20')

        def escurecer(rgba, fator=0.7):
            r, g, b, a = rgba
            h, l, s = colorsys.rgb_to_hls(r, g, b)
            l = max(0, min(1, l * fator))          # diminui a luminosidade
            r2, g2, b2 = colorsys.hls_to_rgb(h, l, s)
            return (r2, g2, b2, a)

        return [escurecer(cmap(i / max(n, 1))) for i in range(n)]

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
                messagebox.showinfo("Sucesso",
                                    f"{len(self.dados_reais)} erros carregados.")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao ler o arquivo: {e}")

    def executar(self):
        self._cancel_requested = False
        self.disable_ui_during_run()
        self._thread_worker = threading.Thread(target=self._processar_simulacao)
        self._thread_worker.start()

    def _ask_continue(self, tempo_total):
        self._continue_resp = None

        def _callback():
            resp = messagebox.askyesno(
                "Tempo estimado",
                f"Tempo estimado: {int(tempo_total)} s.\nDeseja continuar?"
            )
            self._continue_resp = resp

        self.master.after(0, _callback)

        while self._continue_resp is None:
            time.sleep(0.05)
        return self._continue_resp

    def _finalizar_thread(self, cancelado: bool):
        def _restore():
            self.enable_ui_after_run()
            if cancelado:
                messagebox.showinfo("Cancelado", "A simulação foi interrompida.")
        self.master.after(0, _restore)

    def _processar_simulacao(self):
        try:
            N = int(self.entries["Número de PCs"].get())
            erro_admissivel = float(self.entries["Erro admissível (PEC)"].get())
            perc_base = int(self.entries["% PCs acima do PEC"].get())
            intervalo_acima = int(self.entries["Intervalo acima (%)"].get())
            intervalo_abaixo = int(self.entries["Intervalo abaixo (%)"].get())
            n_iter = int(self.entries["Nº de iterações"].get())

            self.percentuais = list(range(intervalo_abaixo,
                                         intervalo_acima + 2, 2))
            self.tamanhos_amostra = list(range(5,
                                              int(N * 0.6) + 1, 5))

            base_teste = gerar_tabela_base(N, erro_admissivel, perc_base)
            tempo_unit = simular_percentual_rejeicao(
                base_teste, self.tamanhos_amostra, n_iter,
                erro_admissivel, perc_base, tempo_estimado=True)

            tempo_total = tempo_unit * len(self.percentuais)

            if not self._ask_continue(tempo_total):
                self._finalizar_thread(cancelado=True)
                return

            self.inicio_processamento = time.time()
            self.curvas_precisao.clear()
            self.curvas_norma.clear()

            for perc in self.percentuais:
                if self._cancel_requested:
                    self._finalizar_thread(cancelado=True)
                    return

                base = gerar_tabela_base(N, erro_admissivel, perc)
                pr_p, pr_n = simular_percentual_rejeicao(
                    base, self.tamanhos_amostra, n_iter,
                    erro_admissivel, perc,
                    progress_callback=self.atualizar_progresso)

                self.curvas_precisao.append(pr_p)
                self.curvas_norma.append(pr_n)

            if self.dados_reais:
                base_real = np.array(self.dados_reais)
                pr_p_r, pr_n_r = simular_percentual_rejeicao(
                    base_real, self.tamanhos_amostra, n_iter,
                    erro_admissivel, perc_base)
                self.curva_precisao_R = pr_p_r
                self.curva_norma_R = pr_n_r

            self.tempo_processamento = time.time() - self.inicio_processamento

            self.master.after(0, self.plotar)

            self._finalizar_thread(cancelado=False)

        except Exception as exc:
            self.master.after(0, lambda: messagebox.showerror(
                "Erro", f"Ocorreu um erro inesperado: {exc}"))
            self._finalizar_thread(cancelado=True)

    def plotar(self):
        fig, ax = plt.subplots(1, 2, figsize=(14, 6))
        n_curvas = len(self.percentuais)
        cores = self._gerar_cores(n_curvas)

        for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_precisao)):
            ax[0].plot(self.tamanhos_amostra, curva,
                       label=f"{perc}%", color=cores[i], linewidth=_line_width())

        if self.curva_precisao_R is not None:
            ax[0].plot(self.tamanhos_amostra, self.curva_precisao_R,
                       label="R", linewidth=_line_width() * 1.2, color='black')

        ax[0].set_title("Curvas de Rejeição – Precisão")
        ax[0].set_xlabel("Tamanho da Amostra")
        ax[0].set_ylabel("PRM (%)")
        ax[0].legend()
        ax[0].grid(True)

        for i, (perc, curva) in enumerate(zip(self.percentuais, self.curvas_norma)):
            ax[1].plot(self.tamanhos_amostra, curva,
                       label=f"{perc}%", color=cores[i], linewidth=_line_width())

        if self.curva_norma_R is not None:
            ax[1].plot(self.tamanhos_amostra, self.curva_norma_R,
                       label="R", linewidth=_line_width() * 1.2, color='black')

        ax[1].set_title("Curvas de Rejeição – Norma Brasileira")
        ax[1].set_xlabel("Tamanho da Amostra")
        ax[1].set_ylabel("PRM (%)")
        ax[1].legend()
        ax[1].grid(True)

        plt.tight_layout()
        secs = self.tempo_processamento
        mins, secs = divmod(secs, 60)
        tempo_str = f"{int(mins)} min {secs:.1f} s" if mins else f"{secs:.1f} s"

        fig.text(0.58, 0.98,
                 f"Tempo total: {tempo_str}",
                 ha='right', va='top',
                 fontsize=10,
                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='gray'))

        plt.show(block=False)
        self.figura = fig

    def exportar_planilha(self):
        if not self.curvas_precisao:
            messagebox.showwarning("Aviso", "Execute a simulação antes.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Planilha Excel", "*.xlsx")]
        )
        if not caminho:
            return

        try:
            with pd.ExcelWriter(caminho) as writer:
                for i, perc in enumerate(self.percentuais):
                    df_prec = pd.DataFrame({
                        "Tamanho da Amostra": self.tamanhos_amostra,
                        "PRM (%)": self.curvas_precisao[i]
                    })
                    df_prec.to_excel(writer,
                                     sheet_name=f"Precisao_{perc}%",
                                     index=False)

                    df_norm = pd.DataFrame({
                        "Tamanho da Amostra": self.tamanhos_amostra,
                        "PRM (%)": self.curvas_norma[i]
                    })
                    df_norm.to_excel(writer,
                                     sheet_name=f"Norma_{perc}%",
                                     index=False)

                if self.curva_precisao_R is not None:
                    df_prec_r = pd.DataFrame({
                        "Tamanho da Amostra": self.tamanhos_amostra,
                        "PRM (%)": self.curva_precisao_R
                    })
                    df_prec_r.to_excel(writer,
                                       sheet_name="Precisao_R",
                                       index=False)

                if self.curva_norma_R is not None:
                    df_norm_r = pd.DataFrame({
                        "Tamanho da Amostra": self.tamanhos_amostra,
                        "PRM (%)": self.curva_norma_R
                    })
                    df_norm_r.to_excel(writer,
                                       sheet_name="Norma_R",
                                       index=False)

            messagebox.showinfo("Exportação", "Planilha salva com sucesso!")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao salvar a planilha: {exc}")

    def exportar_grafico(self):
        if not self.figura:
            messagebox.showwarning("Aviso", "Execute a simulação antes.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Imagem PNG", "*.png")]
        )
        if not caminho:
            return

        try:
            self.figura.savefig(caminho, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Salvo", "Gráfico salvo com sucesso!")
        except Exception as exc:
            messagebox.showerror("Erro", f"Falha ao salvar o gráfico: {exc}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimulaPECApp(root)
    root.mainloop()