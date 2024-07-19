from flask import Flask
from flask_restx import Api

from board.pages import bp as pages_bp
from board.video import bp_video

def create_app():
    app = Flask(__name__)

    app.register_blueprint(pages.bp)
    app.register_blueprint(bp_video)

    # Flask-RestX API 객체 초기화
    api = Api(
        app,
        version='1.0',
        title='Lucky Vicky Geti Viti API',
        description='APIs for Lucky Vicky Geti Viti operations',
        doc='/api-docs'  # API 문서 경로 설정
    )

    return app

app = create_app()