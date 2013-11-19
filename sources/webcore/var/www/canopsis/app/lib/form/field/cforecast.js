/*
# Copyright (c) 2013 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
*/

Ext.define('canopsis.lib.form.field.cforecast' , {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.cforecast',

	layout: 'vbox',

	enable: false,
	max_points: 250,
	max_points_min: 1,

	duration = {value: 1, unit: 'day'},
	number_step: 1,
	number_min_val: 0,

	value: {unit: 'day', value: 1},
	add_none_value: false,

	fieldLabel: undefined,

	Custom = {category: "Custom", demand: 0, beta: 0, trend: 0},
	NotLinearMidVariable = {category:"Not linear mid variable", demand:0.99, beta:0.12, trend:0.80},
	LinearNotVariable = {category:"Linear not variable", demand:0.99, seasonality:0.01, trend:0.97},
	NotLinearVariable = {category:"Not linear variable", demand:0.60, seasonality:1, trend:0.01},
	LinearVariable = {category:"Linear variable", demand:0.68, seasonality:0.01, trend:0.17},

	category = this.NotLinearMidVariable,

	demand: 0.99,
	seasonality: 0.12,
	trend: 0.8,

	critical_threshold: 0,
	warning_threshold: 0,

	initComponent: function() {
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_enable = Ext.widget('checkbox', {
			name: 'forecast_enable',
			checked: this.enable,
			labelField: 'Enable',
		});
		this.ts_max_points = Ext.widget('numberfield', {
			name: 'forecast_max_points',
			width: 50,
			value: this.max_points,
			minValue: this.max_points_min,
			labelField: 'Max points'
		});
		this.ts_duration = Ext.widget('cperiod', {
			isFormField: false,
			name: 'ts_duration',			
			value:this.duration,
			minValue: this.number_min_val,
			fieldLabel: 'Duration (if no max points)'
		});
		this.ts_date = Ext.widget('datefield', {
			name: 'date',
			value: this.date,
			fieldLabel: 'End date (if no max points and no duration',
		});

		var category_store_data [
			{'name': _(NotLinearMidVariable.category), 'value': NotLinearMidVariable},
			{'name': _(LinearNotVariable.category), 'value': LinearNotVariable},
			{'name': _(LinearVariable.category), 'value': LinearVariable},
			{'name': _(LinearVariable.category), 'value': LinearVariable},
			{'name': _(Custom.category), 'value': Custom},
		];

		// algorithm parametes
		this.ts_category = Ext.widget('combobox', {
			isFormField: false,
			editable: false,
			width: 97,
			name: 'category',
			queryMode: 'local',
			displayField: 'name',
			valueField: 'value',
			labelField: 'Category',
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: category_store_data
			}
		});
		this.ts_demand = Ext.widget('numberfield', {
			name: 'demand',
			value: this.demand,
			fieldLabel: 'Demand (alpha)'
		});
		this.ts_seasonality = Ext.widget('numberfield', {
			name: 'seasonality',
			value: this.seasonality,
			fieldLabel: 'Seasonality (beta)'
		});
		this.ts_trend = Ext.widget('numberfield', {
			name: 'trend',
			value: this.trend,
			fieldLabel: 'Trend (gamma)'
		});
		this.ts_trend = Ext.widget('numberfield', {
			name: 'trend',
			value: this.trend,
			fieldLabel: 'Trend (gamma)'
		});
		this.ts_warning_threshold = Ext.widget('numberfield', {
			name: 'warning_threshold',
			value: this.warning_threshold,
			fieldLabel: 'Warning Threshold'
		});
		this.ts_critical_threshold = Ext.widget('numberfield', {
			name: 'critical_threshold',
			value: this.critical_threshold,
			fieldLabel: 'Critical threshols'
		});
		this.items = [
			this.ts_enable, 
			this.ts_max_points, 
			this.ts_duration, 
			this.ts_date,
			this.ts_category,
			this.ts_demand,
			this.ts_seasonality,
			this.ts_trend,
			this.ts_warning_threshold,
			this.ts_critical_threshold
		];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		if(value[0].raw.value) {
			this.ts_window.setDisabled(false);
		}
		else {
			this.ts_window.setDisabled(true);
		}
	},

	show: function() {
		this.callParent(arguments);
		for (int i=1; i<this.items.length; i++) {
			item = this.items[i];
			item.show();
			item.setDisabled(false);
		};
	},

	hide: function() {
		this.callParent(arguments);
		for (int i=1; i<this.items.length; i++) {
			item = this.items[i];
			item.hide();
			item.setDisabled(true);
		};
	},

	getValue: function() {
		result = {};

		for (int i=1; i<this.items.length; i++) {
			item = this.items[i];
			result[item.getName()] = item.getValue();
		};

		return result;
	},

	setValue: function(value) {
		if(value) {

		}
		else {
			this.ts_unit.select(this.ts_unit.getStore().data.items[0]);
		}
	}
});
