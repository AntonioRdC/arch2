# Mapa de configuração

Este documento é um índice curto para humanos e IAs. Os caminhos abaixo são relativos à raiz do repositório e correspondem ao destino dentro de `/home/ant` quando ficam sob `home/`.

## Sessão gráfica

| Caminho | Função |
| --- | --- |
| `home/.config/hypr/hyprland.lua` | Ponto de entrada do Hyprland; importa os módulos Lua. |
| `home/.config/hypr/config/monitors.lua` | Painel interno a 240 Hz, escala 1 e monitor externo preferido. |
| `home/.config/hypr/config/input.lua` | Layouts `br,us`, teclado ABNT2 como primeiro layout, touchpad e cursor. |
| `home/.config/hypr/config/appearance.lua` | Gaps, bordas, animações, blur, arredondamento e fundo padrão desativado. |
| `home/.config/hypr/config/keybinds.lua` | Keybinds de aplicativos, Rofi, energia, jogos, screenshots, mídia e teclas Alienware. |
| `home/.config/hypr/config/rules.lua` | Flutuação de diálogos, VLC e picture-in-picture. |
| `home/.config/hypr/themes/catppuccin-mocha.lua` | Tokens de cor usados pelo Hyprland. |
| `home/.config/waybar/` | Configuração JSONC, CSS e tema Mocha; inclui CPU/GPU, memória, bateria e áudio. |
| `home/.config/rofi/` | Temas Catppuccin e layouts de apps, jogos, energia e wallpaper. |
| `home/.config/dunst/dunstrc` | Notificações. |
| `home/.config/systemd/user/` | Inicialização coordenada de Waybar, awww, iluminação e Polkit. |
| `system/sddm/` | Tema Astronaut/Violet Evergarden e configuração usada pelo SDDM. |

## Terminal e arquivos

| Caminho | Função |
| --- | --- |
| `home/.zshrc` | PATH, plugins Zsh, FZF, zoxide, Starship, aliases e Fastfetch no Kitty. |
| `home/.bashrc`, `home/.bash_profile` | Fallback para sessões Bash e inicialização do NVM quando instalado. |
| `home/.config/kitty/` | Kitty e cores Catppuccin Mocha. |
| `home/.config/fastfetch/` | Layout de informações do sistema e ícone ASCII. |
| `home/.config/yazi/` | Gerenciador de arquivos, tema Catppuccin e abridores de imagem, mídia, PDF e Wine. |
| `home/.config/swayimg/init.lua` | Visualizador de imagens sem overlay, com navegação pelas setas. |
| `home/.config/vlc/vlcrc` | VLC minimalista com decodificação `vaapi_drm`. |
| `home/.config/bat/`, `btop/`, `eza/` | Temas e preferências das ferramentas de terminal. |

## Tema e integração de aplicativos

| Caminho | Função |
| --- | --- |
| `home/.config/gtk-3.0/`, `gtk-4.0/` | Preferência dark, ícones Tela-circle e variáveis Catppuccin/libadwaita. |
| `home/.config/qt5ct/`, `qt6ct/`, `Kvantum/`, `kdeglobals` | Paleta, estilo e ícones Catppuccin para Qt/KDE. |
| `home/.config/spicetify/` | Sleek ativo e port Catppuccin do Spotify. |
| `home/.config/Code - OSS/User/settings.json` | Tema e preferências do editor; histórico e estado do VS Code foram excluídos. |
| `home/.config/mimeapps.list` | Yazi como gerenciador de diretórios e swayimg para imagens. |
| `home/.local/share/applications/` | Entradas e overrides intencionais para o menu de aplicativos. |

## Scripts próprios

- `rofi-apps`, `rofi-games`, `rofi-wallpaper`, `rofi-power`: interfaces acionadas pelos keybinds.
- `toggle-power-profile`, `toggle-quiet-profile`, `toggle-touchpad`: ações das teclas Alienware.
- `waybar-temp`: leitura de temperaturas do `alienware_wmi` para a Waybar.
- `alien-light` e `home/.local/lib/alienware-control/control.py`: controle da iluminação (o binário `alienfx-cli` é externo ao repositório).
- `wine`: wrapper para locale japonês.
- `capture-alienware-keys`: diagnóstico opcional; requer o pacote `evtest`, que não está instalado atualmente.

