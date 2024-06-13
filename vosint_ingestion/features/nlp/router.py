from flask import Blueprint

from .nlpcontroller import NlpController


feature = Blueprint('Nlp', __name__)
nlp_controller = NlpController()

@feature.route('/api/nlp_chude/', methods=['GET'])
def nlp_chude():
    return nlp_controller.nlp_chude()