# ⚛️ J.A.R.V.I.S. System Interface (Front-End V1.0)

> **"Às vezes, é preciso correr antes de andar." — Tony Stark**

Bem-vindo à documentação oficial do Front-end da interface J.A.R.V.I.S. Este projeto é uma aplicação **React + Three.js** altamente otimizada para criar uma experiência de HUD (Heads-Up Display) cinematográfica, reativa e imersiva.

---

## 🛠 Tech Stack (Tecnologias)

* **Core:** React 18 (Vite)
* **Estilização:** Tailwind CSS (para UI, Grids, Tipografia e Animações CSS)
* **3D Engine:** Three.js (`@react-three/fiber`)
* **Helpers 3D:** Drei (`@react-three/drei`) - Usado para `Sparkles` e utilitários.
* **Pós-Processamento:** React Postprocessing (`@react-three/postprocessing`) - Usado para Bloom, Noise, Vignette e Glitch.

---

## 📂 Estrutura do Projeto

O projeto segue uma arquitetura modular onde cada "peça" do HUD é um componente isolado.

```bash
src/
├── components/
│   ├── ArcReactor.jsx       # O container principal que une o núcleo 3D e os anéis
│   ├── ParticleSphere.jsx   # O CORAÇÃO DO SISTEMA (Three.js, Deformação, Shaders)
│   ├── TechRings.jsx        # Anéis rotativos vetoriais (SVG/CSS)
│   ├── HoloFrame.jsx        # Moldura estrutural ("Capacete") que conecta a UI
│   ├── AudioWave.jsx        # Osciloscópio de rodapé (SVG animado via JS)
│   ├── LiveTelemetry.jsx    # Widgets de dados (CPU, Rede) nos cantos inferiores
│   ├── StartupScreen.jsx    # Sequência de Boot (Loading tático)
│   ├── Typewriter.jsx       # Efeito de digitação para textos
│   └── CustomCursor.jsx     # Cursor de mouse personalizado (Mira Tática)
├── App.jsx                  # Gerenciador de Estados (Idle, Listen, Speak)
└── index.css                # Estilos globais, fontes e animações Keyframes (scanlines)

```

---

## 📘 Guia Detalhado dos Componentes

### 1. `ParticleSphere.jsx` (O Núcleo)

Este é o componente mais complexo. Ele renderiza milhares de pontos em um espaço 3D.

* **Lógica de Deformação:** Utiliza manipulação direta de vértices (`bufferAttribute`) dentro de um hook `useFrame` para performance máxima.
* **Estados:**
* `IDLE`: Rotação suave, cor ciano.
* `LISTENING`: Esfera contrai, fica branca, rotação lenta (foco).
* `SPEAKING`: Deformação senoidal (ondas), cor elétrica, rotação rápida.

* **Efeitos Visuais:**
* **Bloom:** Brilho neon.
* **Sparkles:** Poeira volumétrica no ambiente.
* **Chromatic Aberration:** Separação de cores RGB nas bordas (efeito de lente).
* **Noise:** Granulação de filme para realismo.

* **Parallax:** A esfera segue suavemente a posição do mouse (olhar do robô).

### 2. `TechRings.jsx` & `HoloFrame.jsx`

Responsáveis pela "Ancoragem Visual".

* Usam SVG e CSS puro para garantir linhas nítidas (vetoriais) que não serrilham.
* Animações de rotação são feitas via classes do Tailwind (`animate-spin`).

### 3. `LiveTelemetry.jsx`

Simula dados reais.

* Usa `setInterval` para gerar números aleatórios dentro de ranges realistas (ex: Temp CPU 40-65°C).
* Puramente estético para dar "vida" aos cantos da tela.

---

## 🎛 Como Customizar (Manual de Ajustes)

Aqui está onde você deve mexer para alterar o comportamento do JARVIS:

### 🎨 Mudar Cores e Intensidade do Brilho

Vá em `src/components/ParticleSphere.jsx`. Procure o objeto `config`:

```javascript
const config = {
  idle: { coreColor: "#4fd1c5", bloom: 1.5 },     // Cor padrão
  listening: { coreColor: "#ffffff", bloom: 0.8 }, // Cor ao ouvir
  speaking: { coreColor: "#00eaff", bloom: 3.0 },  // Cor ao falar
};

```

### ⚡ Ajustar a "Loucura" da Deformação (Modo Speak)

Vá em `src/components/ParticleSphere.jsx` dentro do `useFrame`.
Procure as variáveis `wave1`, `wave2` e `distortion`.

* Aumente os multiplicadores de `time` para ondas mais rápidas.
* Aumente o multiplicador final (ex: `* 0.4`) para picos mais altos na esfera.

### 🎥 Ajustar o "Look de Cinema" (Sujeira/Lente)

Vá no final de `ParticleSphere.jsx` dentro de `<EffectComposer>`:

* **Granulação:** Altere `<Noise opacity={0.02} />`. (0.02 é limpo, 0.1 é TV velha).
* **Falha de Cor:** Altere `<ChromaticAberration offset={[0.002, 0.002]} />`.

### ⏱ Ajustar Velocidade de Digitação

No arquivo `src/App.jsx`, onde o componente `<Typewriter />` é chamado:

```jsx
<Typewriter text={message} speed={30} /> // Menor = Mais rápido

```

---

## 🚀 Instalação e Execução

Para rodar este projeto em qualquer máquina nova:

1.**Instale as dependências:**

```bash
npm install
```

2.**Rode o servidor de desenvolvimento:**

```bash
npm run dev
```

3.**Build para Produção:**

```bash
npm run build
```

---

## ⚠️ Notas Importantes

* **Performance:** O componente `ParticleSphere` manipula 7.000 pontos a 60FPS. Embora otimizado, máquinas sem placa de vídeo dedicada podem ter leve queda de performance com o **Bloom** ativado.
* **Cursor:** O cursor do mouse é ocultado globalmente pelo componente `CustomCursor`. Se precisar do cursor padrão para debug, comente o componente no `App.jsx`.

---

**J.A.R.V.I.S Project © 2025 - J.A.R.V.I.S. Protocol FRONT-END**