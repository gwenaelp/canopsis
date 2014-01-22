define(function(require, exports, module) {
	Ember.TEMPLATES['accounts'] = Ember.Handlebars.compile(require('text!app/templates/accounts.html'));

	var Application = require('app/application');

	Application.AccountsRoute = Ember.Route.extend({
		setupController: function(controller, model) {
			controller.set('content', model);
			controller.set('route', this);
		},

		model: function() {
			var me = this;

			return $.ajax({
				url: '/account/',
				type: 'GET',
				contentType: 'application/json',
			}).then(function(data, status, xhr) {
				var accounts = [];

				var group_prefix = 'group.';

				for(var i = 0; i < data.data.length; i++) {
					var account = data.data[i];

					var groups = [];

					for(var j = 0; j < account.groups.length; j++) {
						groups.push(account.groups[j].substring(group_prefix.length));
					}

					accounts.push({
						enable: account.enable,
						id: account.id,
						user: account.user,
						firstname: account.firstname,
						lastname: account.lastname,
						mail: account.mail,
						group: account.aaa_group.substring(group_prefix.length),
						groups: groups
					});
				}

				/* return final model */
				var controller = me.controllerFor('accounts');

				return {
					'toolitems': controller.toolbar,
					'accounts': accounts
				};
			});
		}
	});

	Application.AccountsController = Ember.ObjectController.extend({
		toolbar: [{
			title: 'Refresh',
			action: 'refresh',
			icon: 'refresh'
		},{
			title: 'Add',
			action: 'add',
			icon: 'plus-sign'
		},{
			title: 'Duplicate',
			action: 'duplicate',
			icon: 'file'
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
				var controller = this;
				var route = this.get('route');

				route.model().then(function(model) {
					controller.set('content', model);
					controller.set('route', route);
				});
			},

			add: function() {
				;
			},

			duplicate: function() {
				;
			},

			remove: function() {
				;
			}
		}
	});
});