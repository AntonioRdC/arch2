# Tema do SDDM

`sddm-astronaut-violet/` é a cópia do tema customizado que está sendo usado na máquina. O arquivo `30-astronaut-theme.conf` seleciona o tema e o backend da entrada Qt.

Para restaurar manualmente:

```sh
sudo install -d /usr/share/sddm/themes
sudo rsync -a sddm-astronaut-violet/ /usr/share/sddm/themes/sddm-astronaut-violet/
sudo install -Dm644 30-astronaut-theme.conf /etc/sddm.conf.d/30-astronaut-theme.conf
sudo systemctl restart sddm
```

A cópia inclui o vídeo de fundo escolhido e as fontes do tema. Faça a instalação quando o SDDM não estiver em uso ou reinicie a sessão depois.

