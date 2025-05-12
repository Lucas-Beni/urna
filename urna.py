import tkinter as tk
from tkinter import messagebox

candidatos = []
votacao_ativa = False

janela = tk.Tk()
frame_topo = tk.Frame(janela)
frame_menu = tk.Frame(janela)
frame_voto = tk.Frame(janela)

pos_x = (1920 // 2) - (1200 // 2)
pos_y = (1080 // 2) - (800 // 2)

def mostra_menu():
    janela.geometry(f"1200x800+{pos_x}+{pos_y}")
    janela.configure(padx=20, pady=20)

    frame_topo.pack(fill="both", expand=True, pady=20)
    frame_menu.pack(pady=150)

    atualiza_lista_candidatos()

    label_menu = tk.Label(frame_menu, text="Escolha uma opção:", font=("Arial", 16))
    label_menu.pack(pady=20)

    botao_cadastro = tk.Button(frame_menu, text="Cadastro de Candidato", command=cadastra_candidato, relief="groove")
    botao_cadastro.pack(pady=5)

    botao_votacao = tk.Button(frame_menu, text="Iniciar Votação", command=iniciar_votacao, relief="groove")
    botao_votacao.pack(pady=5)

    botao_encerrar = tk.Button(frame_menu, text="Encerrar Votação", command=encerrar_votacao, relief="groove")
    botao_encerrar.pack(pady=5)

def atualiza_lista_candidatos():
    # Limpa conteúdo anterior do frame_topo
    for widget in frame_topo.winfo_children():
        widget.destroy()

    if candidatos:
        tk.Label(frame_topo, text="Candidatos disponíveis:", font=("Arial", 14, "bold")).pack(pady=10)
        for c in candidatos:
            texto = f"Candidato: {c['nome']} | Número: {c['numero']} | Partido: {c['partido']}"
            tk.Label(frame_topo, text=texto, font=("Arial", 12)).pack(pady=2)
    else:
        tk.Label(frame_topo, text="Nenhum candidato cadastrado.", font=("Arial", 12, "italic")).pack(pady=10)


def cadastra_candidato():
    janela_cadastro = tk.Toplevel(janela)
    janela_cadastro.title("Cadastro de Candidato")
    janela_cadastro.geometry(f"1200x800+{pos_x}+{pos_y}") # Define o tamanho da janela principal
    tk.Label(janela_cadastro, text="Número do Candidato:").pack(pady=5)
    entrada_numero = tk.Entry(janela_cadastro)
    entrada_numero.pack(pady=5)
    tk.Label(janela_cadastro, text="Nome do Candidato:").pack(pady=5)
    entrada_nome = tk.Entry(janela_cadastro)
    entrada_nome.pack(pady=5)
    tk.Label(janela_cadastro, text="Partido do Candidato:").pack(pady=5)
    entrada_partido = tk.Entry(janela_cadastro)
    entrada_partido.pack(pady=5)

    def salvar_candidato():
        numero = entrada_numero.get()
        nome = entrada_nome.get()
        partido = entrada_partido.get()
        candidatos.append({"numero": numero, "nome": nome, "partido": partido, "votos": 0})
        messagebox.showinfo("Sucesso", "Candidato cadastrado com sucesso!")
        atualiza_lista_candidatos()
        janela_cadastro.destroy()

    botao_salvar = tk.Button(janela_cadastro, text="Salvar",  command=salvar_candidato)
    botao_salvar.pack(pady=5)

def iniciar_votacao():
    global votacao_ativa
    votacao_ativa = True
    registrar_voto()

def registrar_voto():
    if votacao_ativa:
        janela_votacao = tk.Toplevel(janela)
        janela_votacao.title("Votação")
        janela_votacao.geometry(f"1200x800+{pos_x}+{pos_y}") # Define o tamanho da janela principal

        frame_topo.pack(fill="both", expand=True, pady=20)
        frame_voto.pack(pady=150)

        atualiza_lista_candidatos()
    

        tk.Label(janela_votacao, text="Digite sua matrícula:").pack(pady=5)
        entrada_matricula = tk.Entry(janela_votacao)
        entrada_matricula.pack(pady=5)
        tk.Label(janela_votacao, text="Digite o número do candidato:").pack(pady=5)
        entrada_voto = tk.Entry(janela_votacao)
        entrada_voto.pack(pady=5)

        def confirmar_voto():
            matricula = entrada_matricula.get()
            voto = entrada_voto.get()
            if not matricula:
                messagebox.showwarning("Erro", "Matrícula não pode ser vazia.")
                return
            candidato_escolhido = next((c for c in candidatos if c["numero"] == voto), None)
            if candidato_escolhido:
                confirmar = messagebox.askyesno("Confirmação", f"Confirmar voto para {candidato_escolhido['nome']} ({candidato_escolhido['partido']})?")

                if confirmar:
                    candidato_escolhido["votos"] += 1
                    messagebox.showinfo("Sucesso", "Voto registrado com sucesso!")
                    janela_votacao.destroy()
                    registrar_voto()

            else:
                confirmar = messagebox.askyesno("Confirmação", "Candidato inexistente. Confirmar voto nulo?")
                if confirmar:
                    messagebox.showinfo("Sucesso", "Voto nulo registrado!")
                    janela_votacao.destroy()
                    registrar_voto()

        botao_votar = tk.Button(janela_votacao, text="Votar", command=confirmar_voto)
        botao_votar.pack(pady=5)

def imprime_relatorio():
    janela_relatorio = tk.Toplevel(janela)
    janela_relatorio.title("Resultados")
    janela_relatorio.geometry(f"1200x800+{pos_x}+{pos_y}") # Define o tamanho da janela principal
    total_votos = sum(c["votos"] for c in candidatos)
    if total_votos > 0:
        for candidato in candidatos:
            tk.Label(janela_relatorio, text=f"{candidato['nome']} ({candidato['partido']}): {candidato['votos']} votos").pack(pady=5)
    else:
        tk.Label(janela_relatorio, text="Não houve votos válidos.").pack(pady=5)
    botao_fechar = tk.Button(janela_relatorio, text="Fechar", command=janela_relatorio.destroy)
    botao_fechar.pack(pady=5)

def encerrar_votacao():
    global votacao_ativa
    votacao_ativa = False
    imprime_relatorio()

mostra_menu()
janela.mainloop()