define([
	'jquery',
	'app/lib/ember',
	'app/lib/ember-data',
	'app/application'
], function($, Ember, DS, Application) {
	Application.Group = DS.Model.extend({
		name: DS.attr('string'),
		description: DS.attr('string')
	});

	Application.Group.reopenClass({
		findAll: function(store, authkey) {
			return $.ajax({
				url: '/rest/object/group',
				method: 'GET',
				contentType: 'application/json',
				data: {
					authkey: authkey
				}
			});
		},

		extractFindAll: function(store, payload) {
			var groups = [];

			for(var i = 0; i < payload.data.length; i++) {
				var group = payload.data[i];

				group.name = group.crecord_name;

				groups.push(group);
			}

			return groups;
		}
	});

	return Application.Group;
});