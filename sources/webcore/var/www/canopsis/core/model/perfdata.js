define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data',
	'app/application'
], function($, Ember, DS, Application) {
	Application.Perfdata = DS.Model.extend({
		component: DS.attr('string'),
		resource: DS.attr('string'),
		metric: DS.attr('string'),
		unit: DS.attr('string'),
		type: DS.attr('string'),
		retention: DS.attr('number'),
		first_point: DS.attr('number'),
		last_point: DS.attr('number'),
		last_value: DS.attr('number'),
		min: DS.attr('number'),
		max: DS.attr('number'),
		tags: DS.attr('array')
	});

	Application.Perfdata.reopenClass({
		findAll: function(store, authkey) {
			return $.ajax({
				url: '/perfstore',
				method: 'GET',
				contentType: 'application/json',
				data: {
					authkey: authkey
				}
			});
		},

		extractFindAll: function(store, payload) {
			var perfdatas = [];

			for(var i = 0; i < payload.data.length; i++) {
				var perfdata = payload.data[i];

				perfdata.component = perfdata.co;
				perfdata.resource = perfdata.re;
				perfdata.metric = perfdata.me;
				perfdata.unit = perfdata.u;
				perfdata.type = perfdata.t;
				perfdata.retention = perfdata.r;
				perfdata.first_point = perfdata.fts;
				perfdata.last_point = perfdata.lts;
				perfdata.last_value = perfdata.lv;
				perfdata.min = perfdata.mi;
				perfdata.max = perfdata.ma;
				perfdata.tags = perfdata.tg;

				delete perfdata.co;
				delete perfdata.re;
				delete perfdata.me;
				delete perfdata.u;
				delete perfdata.t;
				delete perfdata.r;
				delete perfdata.fts;
				delete perfdata.lts;
				delete perfdata.lv;
				delete perfdata.mi;
				delete perfdata.ma;
				delete perfdata.tg;

				perfdatas.push(perfdata);
			}

			return perfdatas;
		}
	});

	return Application.Perfdata;
});