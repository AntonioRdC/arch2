# Dotfiles — Arch Linux + Hyprland

Configuração pessoal do Arch Linux em `/home/ant`, organizada para ser lida e restaurada por `rsync` ou por outra IA. O conteúdo em `home/` mantém a mesma estrutura da home real; `packages/` contém os manifestos do `pacman`; `system/` contém itens que normalmente ficam fora da home, como o tema do SDDM.

## Conteúdo

- `home/.config/hypr`: Hyprland em Lua, com monitores, entrada, aparência, regras, keybinds e tema Catppuccin.
- `home/.config/waybar`, `rofi`, `dunst`: barra, lançadores de apps/jogos/papel de parede/energia e notificações.
- `home/.config/kitty`, `fastfetch`, `zsh`, `starship.toml`, `bat`, `btop`, `eza`: terminal e ferramentas de shell.
- `home/.config/gtk-*`, `qt5ct`, `qt6ct`, `Kvantum`, `kdeglobals`: tema Catppuccin para GTK/Qt.
- `home/.config/yazi`, `swayimg`, `vlc`: arquivos, imagens, PDFs e vídeo.
- `home/.config/spicetify`: tema Sleek com paleta Catppuccin e os arquivos do port Catppuccin.
- `home/.config/systemd/user`: serviços do awww, Waybar, iluminação Alienware e agente Polkit.
- `home/.local/bin` e `home/.local/lib`: scripts próprios dos keybinds e seus módulos Python.
- `home/.local/share/applications`: overrides `.desktop` usados para limpar e renomear o menu do Rofi.
- `system/sddm`: tema Astronaut customizado com o vídeo/imagem da Violet Evergarden e `30-astronaut-theme.conf`.
- `packages/installed.txt`: todos os pacotes instalados com versão (834 no momento da captura).
- `packages/all-names.txt`: somente os nomes dos 834 pacotes, útil para busca e auditoria.
- `packages/explicit.txt`: pacotes marcados como explicitamente instalados (123).
- `packages/foreign.txt`: pacotes fora dos repositórios oficiais/AUR detectados pelo pacman.
- `packages/orphans.txt`: dependências órfãs no momento da captura.
- `packages/code-extensions.txt`: extensões instaladas no Code - OSS.

## Restaurar em uma instalação equivalente

Faça backup dos arquivos atuais antes de sobrescrever e confira os caminhos específicos da máquina (principalmente `/home/ant` em `qt5ct.conf`, `qt6ct.conf` e alguns `.desktop`). Depois:

```sh
rsync -a home/.config/ "$HOME/.config/"
rsync -a home/.local/bin/ "$HOME/.local/bin/"
rsync -a home/.local/lib/ "$HOME/.local/lib/"
rsync -a home/.local/share/applications/ "$HOME/.local/share/applications/"
```

Para os pacotes oficiais:

```sh
sudo pacman -Syu
sudo pacman -S --needed - < packages/explicit.txt
```

Se `packages/foreign.txt` não estiver vazio, instale esses itens com o gerenciador correspondente (por exemplo, um helper AUR) separadamente. `installed.txt` é inventário, não deve ser usado diretamente para reinstalar versões antigas.

Os serviços de usuário podem ser habilitados após verificar se as dependências existem:

```sh
systemctl --user daemon-reload
systemctl --user enable --now awww-daemon.service awww-wallpaper.service waybar.service alienware-lighting.service
systemctl --user enable --now plasma-polkit-agent.service
```

O tema do SDDM exige privilégios de administrador. O arquivo de referência para instalar o tema e ativá-lo está em `system/sddm/`; não foi criado um script automático para evitar substituir configurações do gerenciador de login sem confirmação.

## O que ficou de fora de propósito

Históricos, caches, bancos de estado, cookies, credenciais do Spotify, perfil do Firefox, NVM completo, dados do Steam/qBittorrent e bytecode Python não são dotfiles reproduzíveis e não foram versionados. Binários locais (`alienfx-cli`, `alienware-control` e `subtitle-studio`) também não entram no Git; apenas os scripts, módulos e configurações necessários foram preservados.

O vídeo da tela de login do SDDM foi mantido porque é um asset deliberadamente escolhido pelo usuário. Para um repositório público, considere Git LFS ou manter esse arquivo fora do Git.
