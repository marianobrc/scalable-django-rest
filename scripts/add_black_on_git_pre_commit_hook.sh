echo "#!/usr/bin/env sh 
black ." > .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit