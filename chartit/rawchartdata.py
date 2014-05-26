#!/usr/bin/env python
# coding: utf-8

import copy
import string
from chartdata import DataPool, PivotDataPool

from django.db.models import Model


class RawDataPool(DataPool):
    """ RawDataPool holds the customized data for chartit.
    """

    def __init__(self, series):
        """Create a RawDataPool object as specified by the ``series``.
        :Arguments:
        - **series** *(list of dict)* - specifies the what data to retrieve
          and where to retrieve it from. It is of the form ::

            [{'options': {
               'source': a list of data. or a Django Model...
               },
             'terms': [
               'a_field_name', ... ,
               or '(a_fild_name, func)' where the data were the results by func
               ],
             'names': [
               'display_name_of_the_field_name', ..., ...
              ],
            },
            ...
            ]

          Where

          - **options** (**required**) - a ``dict``. Any of the `series
            options <http://www.highcharts.com/ref/#series>`_ for the
            Highcharts ``options`` object are valid.

          - **terms** - is a list. Each element in ``terms`` is  a ``str`` of
               the data corresponding to the source
        """

        self.user_input = {}
        self.user_input['series'] = copy.deepcopy(series)
        self.series = self._clean_series(series)

    def _clean_series(self, series):
        d_series = {}
        model_source = []
        for ser in series:
            source = ser['options']['source']
            terms = ser['terms']
            if 'names' in ser:
                names = ser['names']
            else:
                names = None
            for i in range(0, len(terms)):
                ti = terms[i]
                fn = None
                if isinstance(terms[i], tuple):
                    ti, fn = terms[i]
                d_series[ti] = {}
                d_series[ti]['field'] = ti
                if isinstance(source, Model):
                    source_i = getattr(source, ti)
                    if fn:
                        model_source.append(fn(source_i))
                elif isinstance(source, list) and len(source) == len(terms):
                    if fn:
                        source[i] = fn(source[i])
                if names:
                    d_series[ti]['field_alias'] = names[i]
                else:
                    d_series[ti]['field_alias'] = \
                        string.capwords(' '.join(ti.split('_')))

            if isinstance(source, Model):
                source = model_source[:]
                model_source = []
            data = []
            sourcelist = zip(*source)
            for item in sourcelist:
                l = {}
                for j in range(0, len(terms)):
                    tj = terms[j]
                    if isinstance(tj, basestring):
                        l[tj] = item[j]
                    elif isinstance(tj, tuple):
                        tj, _ = terms[j]
                        l[tj] = item[j]
                data.append(l)

            for i in range(0, len(terms)):
                if isinstance(terms[i], basestring):
                    d_series[terms[i]]['_data'] = data
                elif isinstance(terms[i], tuple):
                    ti, _ = terms[i]
                    d_series[ti]['_data'] = data

        return d_series


class RawPivotDataPool(PivotDataPool):
    pass
