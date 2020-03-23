import json

from replay.models import Action

def escape(text):
    "Escape text for string.Template substitution."
    return text.replace('$', '$$')


class RecorderMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        return self.process_response(request, self.get_response(request))

    def process_response(self, request, response):
        "Create Action object based on request and response."
        kwargs = {'indent': 4, 'separators': (',', ': ')}
        method = request.method
        data = json.dumps(getattr(request, method), **kwargs)
        files_names = {key: value.name for key, value in request.FILES.items()}
        files = json.dumps(files_names, **kwargs)
        status_code = response.status_code
        redirect = 300 <= status_code < 400
        response_content = response.content
        try:
            response_content.decode('utf-8')
        except UnicodeDecodeError:
            response_content = ''
        content = response_content if not redirect else getattr(response, 'url', response['Location'])

        Action.objects.create(
            method=method,
            path=escape(request.path),
            data=escape(data),
            files=escape(files),
            status_code=str(status_code),
            content=content,
        )

        return response
