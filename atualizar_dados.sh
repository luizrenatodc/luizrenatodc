#!/usr/bin/env bash
# Atualiza dados/commits.txt (um timestamp por commit seu em 2026) e dados/linguagens.jsonl (uma linha por repositório)
# direto da API do GitHub. Conta repositórios privados também, mas só números e datas saem daqui: nenhum nome vai para o perfil.
# Uso: bash atualizar_dados.sh   (precisa do gh logado)
set -euo pipefail
cd "$(dirname "$0")"
USUARIO=luizrenatodc
mkdir -p dados tmp
cp -f dados/commits.txt "tmp/commits.antes.txt" 2>/dev/null || true
cp -f dados/linguagens.jsonl "tmp/linguagens.antes.jsonl" 2>/dev/null || true

gh api "user/repos?per_page=100&affiliation=owner" --paginate --jq '.[] | select(.fork|not) | .name' | sort > tmp/repos.txt
echo "repositórios (sem forks): $(wc -l < tmp/repos.txt)"

: > tmp/commits.novo.txt
: > tmp/linguagens.novo.jsonl
while read -r repo; do
  repo=${repo%$'\r'}
  [ -z "$repo" ] && continue
  gh api "repos/$USUARIO/$repo/languages" >> tmp/linguagens.novo.jsonl 2>/dev/null || echo '{}' >> tmp/linguagens.novo.jsonl
  echo >> tmp/linguagens.novo.jsonl
  gh api "repos/$USUARIO/$repo/commits?author=$USUARIO&since=2026-01-01T00:00:00Z&per_page=100" --paginate --jq '.[].commit.author.date' >> tmp/commits.novo.txt 2>/dev/null || true
done < tmp/repos.txt

grep -v '^$' tmp/linguagens.novo.jsonl > dados/linguagens.jsonl
sort -r tmp/commits.novo.txt | grep -v '^$' > dados/commits.txt
echo "linguagens: $(wc -l < dados/linguagens.jsonl) repos | commits em 2026: $(wc -l < dados/commits.txt)"
echo "dias com commit: $(cut -c1-10 dados/commits.txt | sort -u | wc -l)"
