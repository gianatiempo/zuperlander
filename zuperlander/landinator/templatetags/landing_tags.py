from django.template import Library
register = Library()


@register.simple_tag(takes_context=True)
def imagen(context, img_name):
    landing = context['landing']
    url = landing.imagenes.filter(name=img_name).first().image.url
    return url


@register.simple_tag(takes_context=True)
def imagen_list(context, starter):
    landing = context['landing']
    lista_url = []
    for img in landing.imagenes.filter(name__startswith=starter):
        lista_url.append(img.image.url)
    return lista_url


@register.simple_tag(takes_context=True)
def adjunto(context, adj_name):
    landing = context['landing']
    url = landing.adjuntos.filter(name=adj_name).first().file.url
    return url
