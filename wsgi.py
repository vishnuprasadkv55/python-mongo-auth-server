import app
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), 'env')
load_dotenv(dotenv_path)

handler = app.create_app()

if __name__ == '__main__':
    print("==Debug Mode==")
    app.create_app().run(debug=True)