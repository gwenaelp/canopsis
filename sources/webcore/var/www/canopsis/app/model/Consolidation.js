/*
#--------------------------------
# Copyright (c) 2011 "Capensis" [http://www.capensis.com]
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
# ---------------------------------
*/
Ext.define('canopsis.model.Consolidation', {
	extend: 'Ext.data.Model',
	fields: [
		{name: '_id'},
		{name: 'id', mapping: '_id'},
		{name: 'crecord_type', defaultValue: 'consolidation'},
		{name: 'mfilter'},
		{name: 'crecord_name'},
		{name: 'display_name', defaultValue: ''},
		{name: 'aaa_access_owner', defaultValue: ['r', 'w']},
		{name: 'aaa_admin_group'},
		{name: 'aaa_access_group', defaultValue: ['r']},
		{name: 'aaa_access_other'},
		{name: 'aaa_group', defaultValue: 'group.CPS_selector_admin'},
		{name: 'aaa_owner'},
		{name: 'loaded', defaultValue: false},
		{name: 'state'},
		{name: 'enable', defaultValue: true},
		{name: 'output', defaultValue: ''},
		{name: 'nb_items'},
		{name: 'type_first'},
		{name: 'type_second'},
		{name: 'duration_aggregation'},
		{name: 'output_engine'},
		{name: 'component'},
		{name: 'resource'} 
	]
});