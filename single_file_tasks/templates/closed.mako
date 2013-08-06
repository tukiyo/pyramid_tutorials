# -*- coding: utf-8 -*- 
<%inherit file="layout.mako"/>

<h1>Closed Task's List</h1>

<ul id="tasks">
% if tasks:
  % for task in tasks:
  <li>
    <span class="name">${task['name']}</span>
    <span class="actions">
      [ <a href="${request.route_url('reopen', id=task['id'])}">reopen</a> ]
    </span>
  </li>
  % endfor
% else:
  <li>There are no open tasks</li>
% endif
  <li class="last">
    <a href="${request.route_url('list')}">task list</a>
  </li>
</ul>
