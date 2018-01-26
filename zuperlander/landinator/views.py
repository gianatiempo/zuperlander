import datetime
import json
import logging
import re
import io as stringIO
import requests
from django.utils.encoding import force_text

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.db import models
from django.http import HttpResponseRedirect, Http404, HttpResponse, \
    HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.template import Context
from django.template import RequestContext
from django.template import Template
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, View
from django.views.generic.detail import SingleObjectMixin
from facebookads import FacebookAdsApi
from facebookads import FacebookSession
from facebookads.exceptions import FacebookRequestError
from slugify import slugify

from landinator.forms.base import DynaFormClassForm
from landinator.models.dyna import DynaFormField
from landinator.models.formulario_dinamico import FormularioDinamico, FacebookFanPage, FacebookAdCode
from landinator.models.formulario_dinamico_tracking import TrackingFormularioDinamico
from landinator.models.landing import Landing
from landinator.templatetags import dynaform_tags
from facebookads.adobjects.lead import Lead

log = logging.getLogger(__name__)
DYNAFORM_SESSION_KEY = getattr(settings, 'DYNAFORM_SESSION_KEY', 'DYNAFORM')

# si cambia la clave de fb todos los tokens dejan de servir, hay que actualizar FB_LONG_LIVED_TOKEN
# con FB_LONG_LIVED_TOKEN actualizado, en update_or_create_all_pages() se actualizan las fan pages con nuevos tokens
# instrucciones en http://stackoverflow.com/questions/17197970/facebook-permanent-page-access-token

FB_API = 'v2.8'                                     # version de la API
FB_USER_ID = 'xxxxxxxxxxxxxxx'                      # id del usuario de mundo lead (mundo.leads.@gmail.com)
FB_APP_ID = 'xxxxxxxxxxxxxxxx'                      # id de la app de fb que llama al webhook
FB_APP_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'  # secret key de la app
FB_LONG_LIVED_TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'


def index():
    return HttpResponse("Hello, are you lost? You shouldn't be here...")


def landing(request, slug):
    land = get_object_or_404(Landing, slug=slug)
    formulario = dynaform_tags.dynaform_form(context=RequestContext(request, locals()), form_slug=land.form.slug,
                                             success_url=land.get_absolute_url() + '?do=gracias')

    template = Template(land.html)
    html = template.render(RequestContext(request, {'landing': land, 'form': formulario}))

    return HttpResponse(html)


def update_or_create(page):
    f, c = FacebookFanPage.objects.update_or_create(nombre=page['name'], fan_page_id=page['id'],
                                                    defaults={'token': page['access_token']})


def update_or_create_all_pages():
    url = 'https://graph.facebook.com/' + FB_API + '/' + FB_USER_ID + '/accounts?access_token=' + FB_LONG_LIVED_TOKEN
    pages = requests.get(url).json()
    while True:
        try:
            [update_or_create(page) for page in pages['data']]  # itero toda la pagina actual
            pages = requests.get(url + '&after=' + pages['paging']['cursors']['after']).json()  # pag siguiente
        except KeyError:
            break  # si pincha, es porque no existe la pagina siguiente y termine


def process_fb_change(change):
    fan_page = FacebookFanPage.objects.get(fan_page_id=change['page_id'])
    my_session = FacebookSession(FB_APP_ID, FB_APP_SECRET, fan_page.token)
    my_api = FacebookAdsApi(my_session)
    FacebookAdsApi.set_default_api(my_api)

    try:
        leadgen = Lead(change['leadgen_id'])
        lead_response = leadgen.remote_read()
    except FacebookRequestError as e:
        print("Leadgen_id ({0})- FacebookRequestError: {1}".format(change['leadgen_id'], e))
        return HttpResponse(json.dumps({'status': 'error', 'code': 400}), content_type='application/json')

    lead_response = lead_response['field_data']

    try:
        form = FacebookAdCode.objects.select_related('formulario').get(code=change['ad_id']).formulario
    except FacebookAdCode.DoesNotExist as e:
        print("Ad_id ({0})- FacebookRequestError: {1}".format(change['ad_id'], e))
        return HttpResponse(json.dumps({'status': 'error', 'code': 400}), content_type='application/json')

    processed_lead = {}
    cont = Context()
    for pair in lead_response:
        key = slugify(pair['name']).replace("-", "_")
        value = pair['values'][0]
        processed_lead[key] = value
        cont.update({key: value})

    processed_lead = json.dumps(processed_lead)

    tracking = TrackingFormularioDinamico(site=Site.objects.get_current(), sender=form.name[:200],
                                          utm_source='Facebook', utm_medium='', utm_campaign='',
                                          object_form=form, sent_by_mail=False)

    tracking.data = processed_lead
    tracking.save()

    recipients = stringIO.StringIO(form.recipient_list)
    recipient_lines = [line.strip('\n\r') for line in recipients.readlines()]
    recipient_list = []

    for line in recipient_lines:
        recipient = line.strip('\n\r')
        name, email = re.split('\s*,\s*', recipient)
        recipient_list.append(force_text((email.strip('\n\r')).strip(' ')))

    cont.update({'now': datetime.datetime.now()})
    form.send_notification_email(ctx=cont, recipient_list=recipient_list,
                                 adf_recipient_list=[form.adf_recipient], ignore_limit=True)
    tracking.sent_by_mail = True
    tracking.save()


@csrf_exempt
def leads(request):
    if request.method == "GET":
        challenge = request.GET['hub.challenge']
        verify_token = request.GET['hub.verify_token']
        if verify_token == 'arielito':
            return HttpResponse(challenge)

    if request.method == "POST":
        update_or_create_all_pages()

        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        [process_fb_change(change=change['value']) for change in data['entry'][0]['changes']]  # proceso changes

        return HttpResponse(json.dumps({'status': 'ok', 'code': 200}), content_type='application/json')


def platform(request):
    html = "<h2>My Platform</h2>\n" \
           "<script>\n" \
           "window.fbAsyncInit = function() {\n" \
           "  FB.init({\n" \
           "    appId      : '" + FB_APP_ID + "',\n" \
           "    xfbml      : true,\n" \
           "    version    : '" + FB_API + "' \n" \
           "  });\n" \
           "  FB.AppEvents.logPageView();\n" \
           "};\n" \
           "" \
           "(function(d, s, id){\n" \
           "  var js, fjs = d.getElementsByTagName(s)[0];\n" \
           "  if (d.getElementById(id)) {return;}\n" \
           "  js = d.createElement(s); js.id = id;\n" \
           "  js.src = '//connect.facebook.net/en_US/sdk.js';\n" \
           "  fjs.parentNode.insertBefore(js, fjs);\n" \
           "}(document, 'script', 'facebook-jssdk'));\n" \
           "" \
           "function subscribeApp(page_id, page_access_token) {\n" \
           "  FB.api(\n" \
           "    '/' + page_id + '/subscribed_apps',\n" \
           "    'post',\n" \
           "    {access_token: page_access_token},\n" \
           "    function(response) {\n" \
           "      console.log('Successfully subscribed page', response);\n" \
           "      console.log('Conexion realizada con exito entre la fan page de facebook y Zuperlander!');\n" \
           "    });\n" \
           "}\n" \
           "" \
           "function myFacebookLogin() {\n" \
           "  FB.login(function(response){\n" \
           "    FB.api('/me/accounts', function(response){\n" \
           "      var pages = response.data;\n" \
           "      var ul = document.getElementById('list');\n" \
           "      for (var i=0, len = pages.length; i < len; i++) {\n" \
           "        var page = pages[i];\n" \
           "        var li = document.createElement('li');\n" \
           "        var a = document.createElement('a');\n" \
           "" \
           "        a.href='#';\n" \
           "        a.onclick = subscribeApp.bind(this, page.id, page.access_token);\n" \
           "        a.innerHTML=page.name;\n" \
           "" \
           "        li.appendChild(a);\n" \
           "        ul.appendChild(li);\n" \
           "      }\n" \
           "    });\n" \
           "  }, {scope: 'manage_pages'});\n" \
           "}\n" \
           "</script>\n" \
           "<button onclick='myFacebookLogin()'>Login with Facebook</button>\n" \
           "<ul id='list'></ul>"

    return HttpResponse(html)


def privacy(request):
    return render(request, 'privacy.html')


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class PermissionRequiredMixin(LoginRequiredMixin):
    pass


class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content, content_type='application/json',
                            **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        return json.dumps(context)


class DynaformMixin(object):
    disable_csrf = False

    def post(self, request, *args, **kwargs):
        object_form_pk = request.POST.get('_object_form_pk')
        url = request.POST.get('_object_form_success_url')

        if not object_form_pk and not url and getattr(request, 'session', False):
            DYNAFORM = request.session.get(DYNAFORM_SESSION_KEY, False)
            if DYNAFORM and DYNAFORM.has_key('pk'):
                object_form_pk = DYNAFORM['pk']
                url = DYNAFORM.get('success_url', False)

        context = Context()
        try:
            form_object = FormularioDinamico.objects.get(pk=object_form_pk)
            form = DynaFormClassForm(
                data=request.POST,
                files=request.FILES,
                request=request,
                context=context,
                object_form=form_object
            )

            if form.is_valid():
                form.save()
                if url:
                    return HttpResponseRedirect(url)

            print('post process', form.errors)

        except FormularioDinamico.DoesNotExist:
            raise Http404

        # Fallback resolution order: POST, GET, dispatch
        superClass = super(DynaformMixin, self)

        if hasattr(superClass, 'post'):
            return superClass.post(request, *args, **kwargs)

        if hasattr(superClass, 'get'):
            return superClass.get(request, *args, **kwargs)

        return superClass.dispatch(request, *args, **kwargs)

    # @ensure_csrf_cookie
    def dispatch(self, *args, **kwargs):
        original = super(DynaformMixin, self)
        if self.disable_csrf:
            response = csrf_exempt(original.dispatch)(*args, **kwargs)
        else:
            response = original.dispatch(*args, **kwargs)
        response['P3P'] = 'CP="Link b"'
        return response


class DynaformViewAJAX(SingleObjectMixin, View):
    """
    Vista generica para usar con dynaform, ajax o algo así
    """

    def get_queryset(self):
        # este metodo ya lo resuelve el MultiSiteBaseModel
        return FormularioDinamico.objects.get_for_lang()

    def post(self, request, *args, **kwargs):
        context = Context()
        form_object = self.get_object()
        form = DynaFormClassForm(data=request.POST, files=request.FILES, request=request, context=context,
                                 object_form=form_object)

        if form.is_valid():
            form.save()
            # si es por ajax devuelve OK
            return HttpResponse(json.dumps({'status': 'ok', 'dt': form.dt.pk, 'code': 200}),
                                content_type='application/json')

        return HttpResponseBadRequest(json.dumps({'status': 'error', 'code': 400, 'errors': form.errors}),
                                      content_type='application/json')


class DynaformChoicesRelatedFieldViewAJAX(JSONResponseMixin, View):
    TOKEN_FORMAT = re.compile('%\((?P<field>[a-z0-9\.\_\-]+)\)s', re.U | re.I)

    def label_from_instance(self, obj, label_format):
        key_fields = self.TOKEN_FORMAT.findall(label_format)
        ret = {}
        for key in key_fields:
            parts = key.split('__')
            val = obj
            for part in parts:
                val = getattr(val, part, '')
                ret.update({key: val})

        return label_format % ret

    def get(self, request, *args, **kwargs):
        field_pk = kwargs.get('field_pk', None)
        related_field_pk = kwargs.get('related_field_pk', None)
        pk = kwargs.get('pk', None)

        try:
            field = DynaFormField.objects.get(pk=field_pk)
        except DynaFormField.DoesNotExist:
            return self.render_to_response({
                'status': 'error',
                'code': 400,
                'errors': 'Field DoesNotExist'
            })

        try:
            related_field = DynaFormField.objects.get(pk=related_field_pk)
        except DynaFormField.DoesNotExist:
            return self.render_to_response({
                'status': 'error',
                'code': 400,
                'errors': 'Related Field DoesNotExist'
            })

        field = field.choices_queryset_queryset()
        related_field_qs = related_field.choices_queryset_queryset()

        try:
            field = field.get(pk=pk)
        except:
            return self.render_to_response({
                'status': 'error',
                'code': 400,
                'errors': 'Choices DoesNotExist'
            })

        qs_args = {}
        for f in related_field_qs.model._meta.fields:
            if f.rel and f.rel.to and isinstance(field, f.rel.to):
                qs_args.update({f.name: field})

        qs = related_field_qs.filter(**qs_args)

        return self.render_to_response({
            'status': 'ok',
            'code': 200,
            'data': [
                (
                    obj.id,
                    related_field.choices_queryset_label
                    and self.label_from_instance(obj,
                                                 related_field.choices_queryset_label) or '%s' % obj
                ) for obj in qs]
        })


class DynaformReportListView(PermissionRequiredMixin, ListView):
    template_name = 'dynaform/report_list.html'
    model = TrackingFormularioDinamico

    def get_queryset(self, *args, **kwargs):
        qs = super(DynaformReportListView, self).get_queryset(*args, **kwargs)
        date_from = datetime.date.today() - datetime.timedelta(30)
        date_to = datetime.date.today()

        options = self.request.GET

        if options.get('date_from'):
            date_from = datetime.datetime.strptime(options['date_from'], '%Y-%m-%d').date()

        if options.get('date_to'):
            date_to = datetime.datetime.strptime(options['date_to'], '%Y-%m-%d').date()

        date_from_ant = date_from - datetime.timedelta(30)
        date_to_ant = date_to - datetime.timedelta(30)

        return qs.values('sender', 'object_form', 'object_form_id').annotate(
            conversiones=models.Count(
                models.Case(models.When(pub_date__range=[date_from, date_to], then='object_form'))),
            conversiones_anterior=models.Count(
                models.Case(models.When(pub_date__range=[date_from_ant, date_to_ant], then='object_form')))
        )


class DynaformReportDetailView(PermissionRequiredMixin, DetailView):
    template_name = 'dynaform/report_detail.html'
    model = FormularioDinamico

    def get_context_data(self, *args, **kwargs):
        context = super(DynaformReportDetailView, self).get_context_data(*args, **kwargs)

        object = self.get_object()
        log.debug("Obtiene el form %s", object.name)

        date_from = datetime.date.today() - datetime.timedelta(30)
        date_to = datetime.date.today()

        options = self.request.GET

        if options.get('date_from'):
            date_from = datetime.datetime.strptime(options['date_from'], '%Y-%m-%d').date()

        if options.get('date_to'):
            date_to = datetime.datetime.strptime(options['date_to'], '%Y-%m-%d').date()

        date_from_ant = date_from - datetime.timedelta(30)
        date_to_ant = date_to - datetime.timedelta(30)

        qs = TrackingFormularioDinamico.objects.filter(object_form=object).extra({
            'year': 'extract(year from pub_date)',
            'month': 'extract(month from pub_date)'
        }) \
            .values('year', 'month') \
            .annotate(conversiones=models.Count('id')) \
            .order_by('year', 'month')

        context['object_list'] = qs
        return context
