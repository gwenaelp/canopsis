//need:app/lib/form/cfield.js
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

Ext.define('canopsis.lib.form.field.cthreshold', {
	extend: 'Ext.form.FieldContainer',
	mixins: ['canopsis.lib.form.cfield'],

	alias: 'widget.cthreshold',

	layout: 'hbox',

	value_step: 1,
	value_min_val: 0,
	value: {value: 10, unit: '%'},

	fieldLabel: "threshold",

	initComponent: function() {
		this.logAuthor = '[' + this.id + ']';
		log.debug('Initialize ...', this.logAuthor);

		this.ts_value = Ext.widget('numberfield', {
			isFormField: false,
			name: 'value',
			value: this.value.value,
			minValue: this.value_min_val,
			step: this.value_step
		});

		var store_data = [
			{'name': _('%'), 'value': '%'},
			{'name': _('None'), 'value': null},
			{'name': _('KILO'), 'value': 'kilo'},
			{'name': _('MEGA'), 'value': 'mega'},
			{'name': _('GIGA'), 'value': 'giga'},
			{'name': _('TERA'), 'value': 'tera'}
		];

		this.ts_unit = Ext.widget('combobox', {
			isFormField: false,
			editable: false,
			name: 'unit',
			queryMode: 'local',
			displayField: 'name',
			valueField: 'value',
			value: this.value.unit,
			store: {
				xtype: 'store',
				fields: ['value', 'name'],
				data: store_data
			}
		});

		this.items = [this.ts_value, this.ts_unit];

		this.callParent(arguments);

		this.setValue(this.value);

	},

	checkDisable: function(combo, value) {
		void(combo);

		if(value[0].raw.value) {
			this.ts_value.setDisabled(false);
		}
		else {
			this.ts_value.setDisabled(true);
		}
	},

	show: function() {
		this.callParent(arguments);
		this.ts_value.show();
		this.ts_value.setDisabled(false);
		this.ts_unit.show();
		this.ts_unit.setDisabled(false);
	},

	hide: function() {
		this.callParent(arguments);
		this.ts_value.hide();
		this.ts_value.setDisabled(true);
		this.ts_unit.hide();
		this.ts_unit.setDisabled(true);
	},

	getValue: function() {
		result = {value: this.ts_value.getValue(), unit: this.ts_unit.getValue()};

		return result;
	},

	setValue: function(value) {
		if(value) {
			this.ts_value.setValue(value.value);
			this.ts_unit.setValue(value.unit);
		}
		else {
			this.setValue(this.value);
		}
	}
});
