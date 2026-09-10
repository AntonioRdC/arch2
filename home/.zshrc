export PATH="$HOME/.local/bin:$PATH"

autoload -Uz compinit
compinit
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

HISTFILE="$HOME/.zsh_history"
HISTSIZE=10000
SAVEHIST=10000
setopt APPEND_HISTORY SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

setopt AUTO_CD INTERACTIVE_COMMENTS
bindkey -e

export PATH="$HOME/.config/nvm/versions/node/v24.20.0/bin:$PATH"

alias ls='eza --icons=auto --group-directories-first'
alias l='eza --icons=auto --group-directories-first -1'
alias ll='eza --icons=auto --group-directories-first -lah --git'
alias la='eza --icons=auto --group-directories-first -a'
alias lt='eza --icons=auto --group-directories-first --tree --level=2'
alias cat='bat --paging=never'
alias less='bat'
alias df='duf'
alias grep='grep --color=auto'

source /usr/share/fzf/completion.zsh
source /usr/share/fzf/key-bindings.zsh
export FZF_DEFAULT_OPTS='--height=40% --layout=reverse --border --color=bg+:#313244,bg:#1e1e2e,spinner:#f5e0dc,hl:#f38ba8 --color=fg:#cdd6f4,header:#f38ba8,info:#cba6f7,pointer:#f5e0dc --color=marker:#b4befe,fg+:#cdd6f4,prompt:#cba6f7,hl+:#f38ba8 --color=selected-bg:#45475a,border:#6c7086,label:#cdd6f4'

source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.plugin.zsh
source /usr/share/zsh/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

eval "$(zoxide init zsh)"

eval "$(starship init zsh)"

source "$HOME/.config/zsh/catppuccin_mocha-zsh-syntax-highlighting.zsh"
source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.plugin.zsh

if [[ "$TERM" == "xterm-kitty" && -z "$FASTFETCH_SHOWN" ]]; then
    export FASTFETCH_SHOWN=1
    fastfetch
fi
