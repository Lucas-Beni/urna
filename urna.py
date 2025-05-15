import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import cv2
import os
import glob
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas
import webbrowser

# Lista de candidatos e controle da votação
candidatos = []
votacao_ativa = False

votos_brancos = 0
votos_nulos = 0

# Criar pasta para armazenar fotos
FOTOS_DIR = "fotos_candidatos"
os.makedirs(FOTOS_DIR, exist_ok=True) # cria a pasta 'fotos_candidatos' para armazenar as fotos de cada candidato

# Janela principal
janela = tk.Tk()
# frame_topo = tk.Frame(janela) # cria a variável frame_topo que armazena toda a lista de candidatos

# Cria um Canvas que contém o bloco e a scrollbar
canvas_frame = tk.Frame(janela, bd=10, relief="groove")

canvas = tk.Canvas(canvas_frame)  # cria o canvas que seria o bloco que contém os candidatos
scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview) # cria a scrollbar para realizar a rolagem do canvas

frame_topo = tk.Frame(canvas) # cria o frame_topo para facilitar o posicionamento dos widgets

frame_topo.bind( # configura para que sempre que ouver uma inserção ou remoção de widgets no frame_topo a função seja ativada para cobrir a nova área
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=frame_topo, anchor="nw") # adiciona o frame_topo como um item dentro do canvas e o posiciona na posição 0,0 em relação a nw(north-west)
canvas.configure(yscrollcommand=scrollbar.set) # cria a ligação entre o canvas e a scrollbar para que o scroll funcione de forma síncrona

def _on_mousewheel(event): # cria a função que será utilizada para que a rolagem da scrollbar funcione com o scroll do mouse
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel) # configura o scroll do mouse para utilizar a função _on_mousewhell

canvas_frame.place(x=20, y=100, width=500, height=650) # posiciona o canvas_frame que contém o canvas e a scrollbar na tela
scrollbar.pack(side="right", fill="y") # posiciona a scrollbar a direita do canvas_frame contendo toda a altura
canvas.pack(side="left", fill="both", expand=True) # posiciona o canvas a esquerda do canvas_frame contendo toda a altura e largura disponiveis com permissão para aumentar de tamanho

frame_menu = tk.Frame(janela) # cria a variável frame_menu que armazena todos os botoes e labels para outras telas

# Centralização da janela
pos_x = (1920 // 2) - (1200 // 2)
pos_y = (1080 // 2) - (800 // 2)

def mostra_menu():
    janela.geometry(f"1200x800+{pos_x}+{pos_y}")
    janela.configure(padx=20, pady=20)

    # REMOVER esta linha:
    # frame_topo.pack(fill="both", expand=True, pady=20)

    atualiza_lista_candidatos()

    candidatos_label = tk.Label(janela, text="Candidatos Disponíveis:", font=("Arial", 20))
    candidatos_label.place(x=20, y=20)

    label_menu = tk.Label(frame_menu, text="Escolha uma opção:", font=("Arial", 20))
    label_menu.place(x=0,y=0)

    botao_cadastro = tk.Button(frame_menu, text="Cadastro de Candidato", command=cadastra_candidato, relief="groove", width=20, height=5)
    botao_cadastro.place(x=50,y=80)

    botao_votacao = tk.Button(frame_menu, text="Iniciar Votação", command=iniciar_votacao, relief="groove", width=20, height=5)
    botao_votacao.place(x=50,y=210)

    botao_encerrar = tk.Button(frame_menu, text="Encerrar Votação", command=encerrar_votacao, relief="groove", width=20, height=5)
    botao_encerrar.place(x=50,y=340)

    frame_menu.place(x=750, y=20, height=650, width=500)

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

    # Frame central para conter todos os widgets
    frame_central = tk.Frame(janela_cadastro)
    frame_central.pack(expand=True)

    tk.Label(frame_central, text="Cadastro de Candidatos", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(20, 40))

    tk.Label(frame_central, text="Número do Candidato:", font=("Arial", 16)).grid(row=1, column=0, sticky="e", pady=20, padx=(20, 20))
    entrada_numero = tk.Entry(frame_central, width=40)
    entrada_numero.grid(row=1, column=1, sticky="w", pady=20, ipady=5)

    tk.Label(frame_central, text="Nome do Candidato:", font=("Arial", 16)).grid(row=2, column=0, sticky="e", pady=20, padx=(20, 20))
    entrada_nome = tk.Entry(frame_central, width=40)
    entrada_nome.grid(row=2, column=1, sticky="w", pady=20, ipady=5)

    tk.Label(frame_central, text="Partido do Candidato:", font=("Arial", 16)).grid(row=3, column=0, sticky="e", pady=20, padx=(20, 20))
    entrada_partido = tk.Entry(frame_central, width=40)
    entrada_partido.grid(row=3, column=1, sticky="w", pady=20, ipady=5)

    foto_caminho = [None]

    def escolher_foto():
        try:
            caminho_original = filedialog.askopenfilename(filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")], parent=janela_cadastro)
            if caminho_original:
                numero = entrada_numero.get().strip()
                nome = entrada_nome.get().strip().replace(" ", "_")
                novo_caminho = os.path.join(FOTOS_DIR, f"{numero}_{nome}.jpg")
                img = Image.open(caminho_original)
                img.save(novo_caminho)
                foto_caminho[0] = novo_caminho
                atualizar_preview(novo_caminho)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar a imagem: {e}")

    def tirar_foto():
        numero = entrada_numero.get().strip()
        nome = entrada_nome.get().strip().replace(" ", "_")

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

    tk.Button(frame_central, text="Escolher Foto", command=escolher_foto, relief="groove", width=20, height=5).grid(row=4, column=0, sticky="e", pady=10, padx=10)
    tk.Button(frame_central, text="Tirar Foto com Webcam", command=tirar_foto, relief="groove", width=20, height=5).grid(row=4, column=1, sticky="w", pady=10, padx=10)

    preview_label = tk.Label(frame_central)
    preview_label.grid(row=5, column=0, columnspan=2, pady=10)

    def salvar_candidato():
        numero = entrada_numero.get()
        nome = entrada_nome.get()
        partido = entrada_partido.get()
        if not numero or not nome or not partido:
            messagebox.showerror("Erro", "Você precisa preencher todos os campos antes de salvar o candidato!")
            return
        else:
            candidatos.append({
                "numero": numero,
                "nome": nome,
                "partido": partido,
                "votos": 0,
                "foto": foto_caminho[0]
            })
            messagebox.showinfo("Sucesso", "Candidato cadastrado com sucesso!")
            atualiza_lista_candidatos()
            janela_cadastro.destroy()

    def limpar_input():
        entrada_numero.delete(0, tk.END)
        entrada_nome.delete(0, tk.END)
        entrada_partido.delete(0, tk.END)

    tk.Button(frame_central, text="Corrige", command=limpar_input, background="red", width=16, height=3).grid(row=6, column=0, sticky="e", pady=10, padx=10)
    tk.Button(frame_central, text="Confirma", command=salvar_candidato, background="green", width=16, height=3).grid(row=6, column=1, sticky="w", pady=10, padx=10)

def iniciar_votacao():
    global votacao_ativa
    votacao_ativa = True
    registrar_voto()

def registrar_voto():
    if votacao_ativa:
        janela_votacao = tk.Toplevel(janela)
        janela_votacao.title("Votação")
        janela_votacao.geometry(f"1200x800+{pos_x}+{pos_y}")

        frame_central2 = tk.Frame(janela_votacao)
        frame_central2.pack(expand=True)

        tk.Label(frame_central2, text="Registro de Voto", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=(20, 40))

        tk.Label(frame_central2, text="Matrícula:", font=("Arial", 16)).grid(row=1, column=0, sticky="e", pady=20, padx=(20, 20))
        entrada_matricula = tk.Entry(frame_central2, width=40)
        entrada_matricula.grid(row=1, column=1, sticky="w", pady=20, ipady=5)

        tk.Label(frame_central2, text="Número do Candidato:", font=("Arial", 16)).grid(row=2, column=0, sticky="e", pady=20, padx=(20, 20))
        entrada_voto = tk.Entry(frame_central2, width=40)
        entrada_voto.grid(row=2, column=1, sticky="w", pady=20, ipady=5)

        preview_label = tk.Label(frame_central2)
        preview_label.grid(row=3, column=0, columnspan=2, pady=20)

        def atualizar_preview(caminho):
            try:
                img = Image.open(caminho)
                img.thumbnail((150, 150))
                img_tk = ImageTk.PhotoImage(img)
                preview_label.configure(image=img_tk)
                preview_label.image = img_tk
            except Exception:
                preview_label.configure(image='', text="(Erro ao carregar imagem)")

        def confirmar_voto():
            matricula = entrada_matricula.get()
            voto = entrada_voto.get()
            if not matricula:
                messagebox.showwarning("Erro", "Matrícula não pode ser vazia.")
                return

            candidato_escolhido = next((c for c in candidatos if c["numero"] == voto), None)

            if candidato_escolhido:
                if candidato_escolhido.get("foto") and os.path.exists(candidato_escolhido["foto"]):
                    atualizar_preview(candidato_escolhido["foto"])
                confirmar = messagebox.askyesno("Confirmação", f"Confirmar voto para {candidato_escolhido['nome']} ({candidato_escolhido['partido']})?")
                if confirmar:
                    candidato_escolhido["votos"] += 1
                    messagebox.showinfo("Sucesso", "Voto registrado com sucesso!")
                    janela_votacao.destroy()
                    registrar_voto()
            else:
                preview_label.configure(image='', text="Candidato não encontrado")
                confirmar = messagebox.askyesno("Confirmação", "Candidato inexistente. Confirmar voto nulo?")
                if confirmar:
                    global votos_nulos
                    votos_nulos += 1
                    messagebox.showinfo("Sucesso", "Voto nulo registrado!")
                    janela_votacao.destroy()
                    registrar_voto()

        
        def corrige():
            entrada_matricula.delete(0, tk.END)
            entrada_voto.delete(0, tk.END)

        def branco():
            global votos_brancos
            branco = messagebox.askyesno("Confirmação", "Confirmar voto em branco?")
            if branco:
                votos_brancos += 1
                messagebox.showinfo("Sucesso", "Voto em branco registrado!")
                janela_votacao.destroy()
                registrar_voto()

        
        frame_botoes = tk.Frame(frame_central2)
        frame_botoes.grid(row=6, column=0, columnspan=2, pady=10)

        tk.Button(frame_botoes, text="Branco", command=branco, background="white", width=16, height=3).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Corrige", command=corrige, background="red", width=16, height=3).pack(side="left", padx=10)
        tk.Button(frame_botoes, text="Confirma", command=confirmar_voto, background="green", width=16, height=3).pack(side="left", padx=10)

def gerar_pdf_resultado():
    nome_pdf = "resultado_votacao.pdf"
    c = Canvas(nome_pdf, pagesize=A4)
    largura, altura = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, altura - 50, "Relatório de Resultado da Votação")

    c.setFont("Helvetica", 14)
    y = altura - 100

    total_votos = sum(c["votos"] for c in candidatos)

    if total_votos > 0 or votos_brancos > 0 or votos_nulos > 0:
        for candidato in candidatos:
            texto = f"{candidato['nome']} ({candidato['partido']}): {candidato['votos']} votos"
            c.drawString(50, y, texto)
            y -= 25

        c.drawString(50, y, f"Votos em Branco: {votos_brancos}")
        y -= 25
        c.drawString(50, y, f"Votos Nulos: {votos_nulos}")
        y -= 25
    else:
        c.drawString(50, y, "Não houve votos válidos.")
        y -= 25

    c.save()

    caminho_absoluto = os.path.abspath(nome_pdf)
    webbrowser.open(f'file://{caminho_absoluto}')

def limpar_fotos():
    for foto in glob.glob(os.path.join(FOTOS_DIR, "*")):
        try:
            os.remove(foto)
        except Exception as e:
            print(f"Erro ao deletar {foto}: {e}")

def encerrar_votacao():
    global votacao_ativa
    votacao_ativa = False
    gerar_pdf_resultado()
    limpar_fotos()


def ao_fechar_janela():
    limpar_fotos()
    nome_pdf = "resultado_votacao.pdf"
    if os.path.exists(nome_pdf):
        try:
            os.remove(nome_pdf)
        except Exception as e:
            print(f"Erro ao deletar {nome_pdf}: {e}")
    janela.destroy()

janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

mostra_menu()

janela.mainloop()