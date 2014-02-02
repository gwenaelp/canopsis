define(['app/lib/ember', 'app/application'], function(Ember, Application) {
	Application.ApplicationRoute = Application.AuthenticatedRoute.extend({
		model: function() {
			return {
				title: 'Canopsis',
				menu: [{
					name: 'Build',
					icon: 'cog',
					links: [
						{url: '/build/accounts', title: 'Accounts', icon: 'user'},
						{url: '/build/groups', title: 'Groups', icon: 'book'},
						{url: '/build/curves', title: 'Curves', icon: 'picture'},
						{url: '/build/perfdata', title: 'PerfData', icon: 'stats'},
						{url: '/build/selectors', title: 'Selectors', icon: 'link'},
						{url: '/build/consolidation', title: 'Consolidation', icon: 'compressed'},
						{url: '/build/topologies', title: 'Topologies', icon: 'tree-conifer'},
						{url: '/build/eventfilter', title: 'Filter Rules', icon: 'filter'}
					]
				},{
					name: 'Run',
					icon: 'play',
					links: [
						{url: '/run/dashboard', title: 'Dashboard', icon: 'dashboard'}
					]
				}]
			};
		}
	});

	Application.ApplicationController = Ember.ObjectController.extend({
		needs: ['login'],

		actions: {
			openTab: function(url) {
				this.transitionToRoute(url);
			},

			logout: function() {
				this.get('controllers.login').setProperties({
					'authkey': null,
					'errors': []
				});

				this.transitionToRoute('/login');
			}
		}
	});

	return Application.ApplicationController;
});