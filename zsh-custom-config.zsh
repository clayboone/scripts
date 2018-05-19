# Tener's custom Zsh file

# env
export EDITOR="vim"

# Source autojump for easy navigation (debian)
if [ -f /usr/share/autojump/autojump.zsh ]; then
	source /usr/share/autojump/autojump.zsh
fi

# Vi-keys in autocomplete
zstyle ':completion:*' menu select
zmodload zsh/complist
bindkey -M menuselect 'h' vi-backward-char
bindkey -M menuselect 'k' vi-up-line-or-history
bindkey -M menuselect 'l' vi-forward-char
bindkey -M menuselect 'j' vi-down-line-or-history

# Don't insert tabs when no chars left of the cursor
zstyle ':completion:*' insert-tab false

# Binds and aliases
bindkey -s '^ ' 'git status --short^M'	# ctrl+space for git status

# Colorful for man pages
man() {
	env \
		LESS_TERMCAP_mb=$(printf "\x1b[38;2;255;200;200m") \
    	LESS_TERMCAP_md=$(printf "\x1b[38;2;255;100;200m") \
    	LESS_TERMCAP_me=$(printf "\x1b[0m") \
    	LESS_TERMCAP_so=$(printf "\x1b[38;2;60;90;90;48;2;40;40;40m") \
    	LESS_TERMCAP_se=$(printf "\x1b[0m") \
    	LESS_TERMCAP_us=$(printf "\x1b[38;2;150;100;200m") \
    	LESS_TERMCAP_ue=$(printf "\x1b[0m") \
    	man "$@"
}

# Attempt to reuse tmux sessions (unless explicitly told to create new)
tmux_cmd=$(which tmux)
tmux() {
	if [ -z $tmux_cmd ]; then
		echo "tmux not installed" 1>&2
		return 1
	fi

	if [ $# -gt 0 ]; then
		$tmux_cmd "$@"
	else
		session=$($tmux_cmd ls | head -n 1 | cut -d: -f1)
		if [ -z $session ]; then
			$tmux_cmd new-session
		else
			$tmux_cmd attach-session -t $session
		fi
	fi
}