define(function(require, exports, module) {
	Ember.TEMPLATES['groups'] = Ember.Handlebars.compile(require('text!app/templates/groups.html'));

	var Application = require('app/application');

	Application.GroupsRoute = Ember.Route.extend({
		model: function() {
			var me = this;

			return $.ajax({
				url: '/rest/object/group',
				method: 'GET',
				contentType: 'application/json'
			}).then(function(data, status, xhr) {
				var groups = [];

				for(var i = 0; i < data.data.length; i++) {
					var group = data.data[i];

					groups.push({
						id: group.id,
						name: group.crecord_name,
						description: group.description
					});
				}

				/* return final model */
				var controller = me.controllerFor('groups');

				return {
					'toolitems': controller.toolbar,
					'groups': groups
				};
			});
		}
	});

	Application.GroupsController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Add',
			action: 'add',
			icon: 'plus-sign'
		},{
			title: 'Remove',
			action: 'remove',
			icon: 'trash'
		}],

		actions: {
			do: function(action) {
				this.send(action);
			},

			refresh: function() {
				console.log('refresh');
			},

			add: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});
});