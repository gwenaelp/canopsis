define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data',
	'app/application'
], function($, Ember, DS, Application) {
	Application.Curve = DS.Model.extend({
		line_color: DS.attr('string'),
		area_color: DS.attr('string'),
		line_style: DS.attr('string'),
		area_opacity: DS.attr('number'),
		zindex: DS.attr('number'),
		invert: DS.attr('boolean'),
		metric: DS.attr('string'),
		label: DS.attr('string')
	});

	Application.Curve.reopenClass({
		findAll: function(store, authkey) {
			return $.ajax({
				url: '/rest/object/curve',
				method: 'GET',
				contentType: 'application/json',
				data: {
					authkey: authkey
				}
			});
		},

		extractFindAll: function(store, payload) {
			var curves = [];

			for(var i = 0; i < payload.data.length; i++) {
				var curve = payload.data[i];

				curve.line_color = '#' + curve.line_color;
				curve.area_color = '#' + curve.area_color;
				curve.line_style = curve.dashStyle;
				curve.zindex = curve.zIndex;

				delete curve.dashStyle;
				delete curve.zIndex;

				curves.push(curve);
			}

			return curves;
		}
	});

	return Application.Curve;
});