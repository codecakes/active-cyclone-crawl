if compgen -G "apps/cyclones/migrations/*" > /dev/null; then
  echo "====clear migrations====";
  python3 manage.py migrate cyclones zero
fi;
echo "=====drop db==========="
./manage.py reset_db -c --noinput;
echo "=====makemigrations====="
python3 manage.py makemigrations && python3 manage.py makemigrations cyclones;
echo "=====migrate====="
python3 manage.py migrate;
python3 manage.py collectstatic --noinput;
echo "======Create Super Admin User====="
python3 manage.py createadmin;
echo "======Run tests========"
python3 manage.py test;
