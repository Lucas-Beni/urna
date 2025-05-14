import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import glob

# Lista de candidatos e controle da votação
candidatos = []
votacao_ativa = False

# Criar pasta para armazenar fotos
FOTOS_DIR = "fotos_candidatos"
os.makedirs(FOTOS_DIR, exist_ok=True) # cria a pasta 'fotos_candidatos' para armazenar as fotos de cada candidato

# Janela principal
janela = tk.Tk()
# frame_topo = tk.Frame(janela) # cria a variável frame_topo que armazena toda a lista de candidatos

# Cria um Canvas com barra de rolagem para candidatos
canvas_frame = tk.Frame(janela)
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, height=300)  # altura limitada para forçar scroll
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)

frame_topo = tk.Frame(canvas)

frame_topo.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame_topo, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)
canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

frame_menu = tk.Frame(janela) # cria a variável frame_menu que armazena todos os botoes e labels para outras telas

# Centralização da janela
pos_x = (1920 // 2) - (1200 // 2)
pos_y = (1080 // 2) - (800 // 2)

def mostra_menu():
    janela.geometry(f"1200x800+{pos_x}+{pos_y}") # define o tamanho e a posição do menu inicial na tela
    janela.configure(padx=20, pady=20) # adiciona um espaçamento nas bordas da tela, impedindo que algo fique incostado na borda

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

    frame_menu.place(x=50, y=500)

def atualiza_lista_candidatos():
    for widget in frame_topo.winfo_children():
        widget.destroy()

    if candidatos:
        tk.Label(frame_topo, text="Candidatos disponíveis:", font=("Arial", 14, "bold")).pack(pady=10)
        for c in candidatos:
            texto = f"Candidato: {c['nome']} | Número: {c['numero']} | Partido: {c['partido']}"
            tk.Label(frame_topo, text=texto, font=("Arial", 12)).pack(pady=2)

            if c.get("foto") and os.path.exists(c["foto"]):
                img = Image.open(c["foto"])
                img.thumbnail((100, 100))
                img_tk = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame_topo, image=img_tk)
                img_label.image = img_tk
                img_label.pack()
    else:
        tk.Label(frame_topo, text="Nenhum candidato cadastrado.", font=("Arial", 12, "italic")).pack(pady=10)

def cadastra_candidato():
    janela_cadastro = tk.Toplevel(janela)
    janela_cadastro.title("Cadastro de Candidato")
    janela_cadastro.geometry(f"1200x800+{pos_x}+{pos_y}")

    tk.Label(janela_cadastro, text="Número do Candidato:").pack(pady=5)
    entrada_numero = tk.Entry(janela_cadastro)
    entrada_numero.pack(pady=5)

    tk.Label(janela_cadastro, text="Nome do Candidato:").pack(pady=5)
    entrada_nome = tk.Entry(janela_cadastro)
    entrada_nome.pack(pady=5)

    tk.Label(janela_cadastro, text="Partido do Candidato:").pack(pady=5)
    entrada_partido = tk.Entry(janela_cadastro)
    entrada_partido.pack(pady=5)

    foto_caminho = [None]

    def escolher_foto():
        caminho_original = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if caminho_original:
            numero = entrada_numero.get().strip()
            nome = entrada_nome.get().strip().replace(" ", "_")
            novo_caminho = os.path.join(FOTOS_DIR, f"{numero}_{nome}.jpg")
            img = Image.open(caminho_original)
            img.save(novo_caminho)
            foto_caminho[0] = novo_caminho
            atualizar_preview(novo_caminho)

    def tirar_foto():
        numero = entrada_numero.get().strip()
        nome = entrada_nome.get().strip().replace(" ", "_")

        if not numero or not nome:
            messagebox.showwarning("Aviso", "Preencha número e nome antes de tirar a foto.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
            return
        ret, frame = cap.read()
        cap.release()
        if ret:
            caminho = os.path.join(FOTOS_DIR, f"{numero}_{nome}.jpg")
            cv2.imwrite(caminho, frame)
            foto_caminho[0] = caminho
            atualizar_preview(caminho)
        else:
            messagebox.showerror("Erro", "Não foi possível capturar a foto.")

    def atualizar_preview(caminho):
        img = Image.open(caminho)
        img.thumbnail((150, 150))
        img_tk = ImageTk.PhotoImage(img)
        preview_label.configure(image=img_tk)
        preview_label.image = img_tk

    tk.Button(janela_cadastro, text="Escolher Foto", command=escolher_foto).pack(pady=5)
    tk.Button(janela_cadastro, text="Tirar Foto com Webcam", command=tirar_foto).pack(pady=5)
    preview_label = tk.Label(janela_cadastro)
    preview_label.pack(pady=5)

    def salvar_candidato():
        numero = entrada_numero.get()
        nome = entrada_nome.get()
        partido = entrada_partido.get()
        candidatos.append({"numero": numero, "nome": nome, "partido": partido, "votos": 0, "foto": foto_caminho[0]})
        messagebox.showinfo("Sucesso", "Candidato cadastrado com sucesso!")
        atualiza_lista_candidatos()
        janela_cadastro.destroy()

    tk.Button(janela_cadastro, text="Salvar", command=salvar_candidato).pack(pady=5)

def iniciar_votacao():
    global votacao_ativa
    votacao_ativa = True
    registrar_voto()

def registrar_voto():
    if votacao_ativa:
        janela_votacao = tk.Toplevel(janela)
        janela_votacao.title("Votação")
        janela_votacao.geometry(f"1200x800+{pos_x}+{pos_y}")

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

        tk.Button(janela_votacao, text="Votar", command=confirmar_voto).pack(pady=5)

def imprime_relatorio():
    janela_relatorio = tk.Toplevel(janela)
    janela_relatorio.title("Resultados")
    janela_relatorio.geometry(f"1200x800+{pos_x}+{pos_y}")
    total_votos = sum(c["votos"] for c in candidatos)
    if total_votos > 0:
        for candidato in candidatos:
            tk.Label(janela_relatorio, text=f"{candidato['nome']} ({candidato['partido']}): {candidato['votos']} votos").pack(pady=5)
    else:
        tk.Label(janela_relatorio, text="Não houve votos válidos.").pack(pady=5)
    tk.Button(janela_relatorio, text="Fechar", command=janela_relatorio.destroy).pack(pady=5)

def limpar_fotos():
    for foto in glob.glob(os.path.join(FOTOS_DIR, "*")):
        try:
            os.remove(foto)
        except Exception as e:
            print(f"Erro ao deletar {foto}: {e}")

def encerrar_votacao():
    global votacao_ativa
    votacao_ativa = False
    imprime_relatorio()
    limpar_fotos()


mostra_menu()
janela.mainloop()