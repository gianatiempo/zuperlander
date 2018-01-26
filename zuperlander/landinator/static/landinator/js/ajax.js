/*
 * Auto-attach ajax for forms
 *
 * usage:
 *
 */

$(function(){

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    $("form[data-ajaxsend]").each(function(){
        var i = new Image();
        i.src = decodeURIComponent('http://s11.postimg.org/lb6hylp9r/loading.gif');
        $(this).append($($("<div class='loading' style='text-align:center' />").append(i)).hide());

        var options = $(this).data('ajaxsend-options');
        if(options){
            options = options.split(';');
            var r = {};
            options.forEach(function(a){
                var b = a.trim().split(':');
                r[b[0]] = (b[1]||'').trim();
                r[b[0]] = r[b[0]] == 'true' ? true : r[b[0]];
                r[b[0]] = r[b[0]] == 'false' ? false : r[b[0]];
                return r
            });
        }

        options = $.extend({
            done_element: this,
            done_event: 'done',
            fail_element: this,
            fail_event: 'fail',
            sending_element: this,
            sending_event: 'sending',
            beforesend_element: this,
            beforesend_event: 'beforesend'
        }, r);

        function disabled(form){
            form.find('input,textarea,select').attr('disabled', true);
        }

        function enabled(form){
            form.find('input,textarea,select').attr('disabled', false);
        }

        $(this).on('submit', function(event){
            var $form = $(this);
            event.preventDefault();

            var xhr = $.ajax({
                type: 'POST',
                url: $form.attr('action'),
                data: $form.serialize(),
                dataType: 'json',
                global: false,
                beforeSend: function(jqXHR){
                    $form.find('.loading').show();
                    disabled($form);
                    $(options.beforesend_element).trigger(options.beforesend_event, jqXHR);
                    if (csrftoken) { jqXHR.setRequestHeader("X-CSRFToken", csrftoken); }
                }
            });

            xhr.always(function(response){
                $form.find('.loading').hide();
                enabled($form);
                $(options.sending_element).trigger(options.sending_event, response);
            });

            xhr.done(function(){
                window.location = $form.find("*[name=_object_form_success_url]").val();
            });

            xhr.fail(function(jqXHR, textStatus, errorThrown){
                $(options.fail_element, $form).trigger(options.fail_event, {jqXHR:jqXHR, textStatus:textStatus, errorThrown:errorThrown});
                try {
                    $.each(jqXHR.responseJSON.errors, function(key, val){
                        $form.find("*[name="+key+"]").addClass('error').next('.error').css('display', 'block').text(val[0]);
                    });
                } catch(E){}
            });

            return false;
        });
    });
});

