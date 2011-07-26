#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
stickon/sqlhtml.py

Classes extending functionality of gluon/sqlhtml.py.

"""
from gluon import *
from gluon.sqlhtml import FormWidget, OptionsWidget, StringWidget

# C0103: Invalid name
# pylint: disable=C0103

class AutoCompleteWidget(object):
    """Alternative for gluon.sqlhtml AutocompleteWidget.

    Note the 'C' is capitalized to distinguish it from the original

    Changes:
        distinct: Passed as a parameter in the select call when retrieving
            records for autocomplete.
        fadeout_duration: integer, jQuery fadeOut duration in ms
        filter_field: gluon.dal.Field, eg db.table.field, autocomplete values
            will be filtered on this field
        filter_input_id: string, css id of input containing filter field value.
        Add z-index to style of DIV
    """

    def __init__(self, request, field, id_field=None, db=None,
                 orderby=None, limitby=(0,10),
                 keyword='_autocomplete_%(fieldname)s',
                 min_length=2, distinct=False,
                 fadeout_duration=600,
                 filter_field=None, filter_input_id='',
                 ):
        self.request = request
        self.keyword = keyword % dict(fieldname=field.name)
        self.db = db or field._db
        self.orderby = orderby
        self.limitby = limitby
        self.min_length = min_length
        self.distinct = distinct
        self.fadeout_duration = fadeout_duration
        self.filter_field = filter_field
        self.filter_input_id = filter_input_id
        self.filter_keyword = ''
        if self.filter_field:
            self.filter_keyword = '_filter_autocomplete_%(fieldname)s' % \
                    dict(fieldname=self.filter_field.name)
            if not self.filter_input_id:
                self.filter_input_id = '%(table)s_%(field)s' % dict(table=self.filter_field.tablename, field=self.filter_field.name)
        self.fields=[field]
        if id_field:
            self.is_reference = True
            self.fields.append(id_field)
        else:
            self.is_reference = False
        if hasattr(request,'application'):
            self.url = URL(r=request, args=request.args)
            self.callback()
        else:
            self.url = request

    def callback(self):
        if self.keyword in self.request.vars:
            field = self.fields[0]
            query = (field.like(self.request.vars[self.keyword]+'%'))
            if self.filter_keyword in self.request.vars and self.request.vars[self.filter_keyword]:
                query = query & (self.filter_field == self.request.vars[self.filter_keyword])
            rows = self.db(query)\
                .select(orderby=self.orderby,limitby=self.limitby,
                distinct=self.distinct, *self.fields)
            if rows:
                if self.is_reference:
                    id_field = self.fields[1]
                    raise HTTP(200,SELECT(_id=self.keyword,_class='autocomplete',
                                          _size=len(rows),_multiple=(len(rows)==1),
                                          *[OPTION(s[field.name],_value=s[id_field.name],
                                                   _selected=(k==0)) \
                                                for k,s in enumerate(rows)]).xml())
                else:
                    raise HTTP(200,SELECT(_id=self.keyword,_class='autocomplete',
                                          _size=len(rows),_multiple=(len(rows)==1),
                                          *[OPTION(s[field.name],
                                                   _selected=(k==0)) \
                                                for k,s in enumerate(rows)]).xml())
            else:
                raise HTTP(200,'')

    def __call__(self, field, value, **attributes):
        default = dict(
            _type = 'text',
            value = (value!=None and str(value)) or '',
            )
        attr = StringWidget._attributes(field, default, **attributes)
        div_id = self.keyword+'_div'
        attr['_autocomplete']='off'
        if self.is_reference:
            key2 = self.keyword+'_aux'
            key3 = self.keyword+'_auto'
            attr['_class']='string'
            name = attr['_name']
            if 'requires' in attr: del attr['requires']
            attr['_name'] = key2
            value = attr['value']
            record = self.db(self.fields[1]==value).select(self.fields[0]).first()
            attr['value'] = record and record[self.fields[0].name]
            attr['_onkeyup'] = "jQuery('#%(key3)s').val('');var e=event.which?event.which:event.keyCode; function %(u)s(){jQuery('#%(id)s').val(jQuery('#%(key)s :selected').text());jQuery('#%(key3)s').val(jQuery('#%(key)s').val())}; if(e==39) %(u)s(); else if(e==40) {if(jQuery('#%(key)s option:selected').next().length)jQuery('#%(key)s option:selected').attr('selected',null).next().attr('selected','selected'); %(u)s();} else if(e==38) {if(jQuery('#%(key)s option:selected').prev().length)jQuery('#%(key)s option:selected').attr('selected',null).prev().attr('selected','selected'); %(u)s();} else if(jQuery('#%(id)s').val().length>=%(min_length)s) jQuery.get('%(url)s?%(key)s='+escape(jQuery('#%(id)s').val()),function(data){if(data=='')jQuery('#%(key3)s').val('');else{jQuery('#%(id)s').next('.error').hide();jQuery('#%(div_id)s').html(data).show().focus();jQuery(document).bind('focusin.%(div_id)s click.%(div_id)s',function(e){if(jQuery(e.target).is('#%(key)s option') || (!jQuery(e.target).closest('##%(id)s,#%(div_id)s').length)){jQuery(document).unbind('.%(div_id)s'); jQuery('#%(div_id)s').fadeOut(%(dur)s)}}); jQuery('#%(div_id)s select').css('width',jQuery('#%(id)s').css('width'));jQuery('#%(key3)s').val(jQuery('#%(key)s').val());jQuery('#%(key)s').change(%(u)s);jQuery('#%(key)s').click(%(u)s);};}); else jQuery('#%(div_id)s').fadeOut('slow');" % \
                dict(url=self.url,min_length=self.min_length,
                     key=self.keyword,id=attr['_id'],key2=key2,key3=key3,
                     name=name,div_id=div_id,u='F'+self.keyword,
                     dur=self.fadeout_duration)
            if self.min_length==0:
                attr['_onfocus'] = attr['_onkeyup']
            return TAG[''](INPUT(**attr),INPUT(_type='hidden',_id=key3,_value=value,
                                               _name=name,requires=field.requires),
                               DIV(_id=div_id,_style='position:absolute; z-index: 99'))
        else:
            attr['_name']=field.name
            filter_str = ''
            if self.filter_keyword and self.filter_input_id:
                filter_str = "+'&%(filter_key)s='+escape(jQuery('#%(filter_id)s').val())" % \
                    dict(url=self.url,min_length=self.min_length,
                         key=self.keyword,id=attr['_id'],div_id=div_id,u='F'+self.keyword,
                         filter_key=self.filter_keyword,
                         filter_id=self.filter_input_id,
                         )
            attr['_onkeyup'] = "var e=event.which?event.which:event.keyCode; function %(u)s(){jQuery('#%(id)s').val(jQuery('#%(key)s').val())}; if(e==39) %(u)s(); else if(e==40) {if(jQuery('#%(key)s option:selected').next().length)jQuery('#%(key)s option:selected').attr('selected',null).next().attr('selected','selected'); %(u)s();} else if(e==38) {if(jQuery('#%(key)s option:selected').prev().length)jQuery('#%(key)s option:selected').attr('selected',null).prev().attr('selected','selected'); %(u)s();} else if(jQuery('#%(id)s').val().length>=%(min_length)s) jQuery.get('%(url)s?%(key)s='+escape(jQuery('#%(id)s').val())%(filter_str)s,function(data){jQuery('#%(id)s').next('.error').hide();jQuery('#%(div_id)s').html(data).show().focus(); jQuery(document).bind('focusin.%(div_id)s click.%(div_id)s',function(e){if(jQuery(e.target).is('#%(key)s option') || (!jQuery(e.target).closest('##%(id)s,#%(div_id)s').length)){jQuery(document).unbind('.%(div_id)s'); jQuery('#%(div_id)s').fadeOut(%(dur)s)}}); jQuery('#%(div_id)s select').css('width',jQuery('#%(id)s').css('width'));jQuery('#%(key)s').change(%(u)s);jQuery('#%(key)s').click(%(u)s);}); else jQuery('#%(div_id)s').fadeOut('slow');" % \
                dict(url=self.url,min_length=self.min_length,
                     key=self.keyword,id=attr['_id'],div_id=div_id,u='F'+self.keyword,
                     filter_str=filter_str,
                     dur=self.fadeout_duration)
            if self.min_length==0:
                attr['_onfocus'] = attr['_onkeyup']
            return TAG[''](INPUT(**attr),DIV(_id=div_id,
                _style='position:absolute; z-index: 99'))


class InputWidget(FormWidget):
    """Custom input widget."""

    def __init__(self, attributes=None, class_extra=''):
        """Constructor.

        Args:
            attributes: dict, dictionary of custom attributes.
            class_extra: string, value appended to _class value.
        """

        # W0221: Arguments number differs from overridden method
        # W0231: __init__ method from base class FormWidget is not called
        # pylint: disable=W0221,W0231

        self.attributes = attributes if attributes else {}
        self.class_extra = class_extra

    def widget(self, field, value, **attributes):
        """Generate INPUT tag for custom widget.

        See gluon.sqlhtml FormWidget
        """
        # W0221: Arguments number differs from overridden method
        # pylint: disable=W0221

        new_attributes = dict(
            _type='text',
            _value=(value != None and str(value)) or '',
            )
        new_attributes.update(self.attributes)
        attr = self._attributes(field, new_attributes, **attributes)
        if self.class_extra:
            attr['_class'] = ' '.join([attr['_class'], self.class_extra])
        return INPUT(**attr)


class SelectWidget(OptionsWidget):
    """Custom select widget."""

    def __init__(self, attributes=None, class_extra=''):
        """Constructor.

        Args:
            attributes: dict, dictionary of custom attributes.
            class_extra: string, value appended to _class value.
        """

        # W0221: Arguments number differs from overridden method
        # W0231: __init__ method from base class FormWidget is not called
        # pylint: disable=W0221,W0231

        self.attributes = attributes if attributes else {}
        self.class_extra = class_extra

    def widget(self, field, value, **attributes):
        """Generate INPUT tag for custom widget.

        See gluon.sqlhtml FormWidget

        Notes:
            Unlike OptionsWidget, this method permits a select to be created
            without options.
        """
        # W0221: Arguments number differs from overridden method
        # pylint: disable=W0221

        options = {}
        requires = field.requires
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                options = requires[0].options()
        opts = [OPTION(v, _value=k) for (k, v) in options]

        new_attributes = dict(
            value=value,
            )
        new_attributes.update(self.attributes)
        attr = self._attributes(field, new_attributes, **attributes)
        if self.class_extra:
            attr['_class'] = ' '.join([attr['_class'], self.class_extra])

        return SELECT(*opts, **attr)
