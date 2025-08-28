cd /d "C:\Users\up739088\Desktop\FMUP\rm4isep\redcap-dashboard-simples"
git init
git remote add origin https://github.com/filipepaulista12/rm4health-dashboard-deploy.git
git add .
git commit -m "Deploy RM4Health Dashboard v2.0"
git push -f origin main
echo PRONTO! Acesse: https://github.com/filipepaulista12/rm4health-dashboard-deploy
