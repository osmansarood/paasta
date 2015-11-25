#!/usr/bin/env python
# Copyright 2015 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Mechanism to rollback to a previous deployed version.
"""
import sys

from paasta_tools.utils import get_git_url
from paasta_tools.paasta_cli.utils import figure_out_service_name
from paasta_tools.paasta_cli.utils import lazy_choices_completer
from paasta_tools.paasta_cli.utils import list_services
from paasta_tools.paasta_cli.utils import list_instances
from paasta_tools.paasta_cli.cmds.mark_for_deployment import mark_for_deployment
from paasta_tools.utils import list_clusters


def add_subparser(subparsers):
    list_parser = subparsers.add_parser(
        'rollback',
        description='Rollback a docker image to a previous deploy',
        help='Rollback a docker image to a previous deploy')

    list_parser.add_argument('-k', '--commit',
                             help='Git sha to mark for rollback',
                             required=True,
                             )
    list_parser.add_argument('-i', '--instance',
                             help='Mark the instance we want to roll back (e.g. '
                             'canary, .main)',
                             required=True,
                             ).completer = lazy_choices_completer(list_instances)
    list_parser.add_argument('-c', '--cluster',
                             help='Mark the cluster we want to rollback (e.g. '
                             'cluster1, cluster2)',
                             required=True,
                             ).completer = lazy_choices_completer(list_clusters)
    list_parser.add_argument('-s', '--service',
                             help='Name of service you wish to rollback'
                             ).completer = lazy_choices_completer(list_services)

    list_parser.set_defaults(command=paasta_rollback)


def paasta_rollback(args):
    """Call mark_for_deployment with rollback parameters"""
    service = figure_out_service_name(args)
    cluster = args.cluster
    instance = args.instance
    git_url = get_git_url(service)
    commit = args.commit

    if cluster in list_clusters(service):
        returncode = mark_for_deployment(
            git_url=git_url,
            cluster=cluster,
            instance=instance,
            service=service,
            commit=commit
        )
    else:
        print "ERROR: The service %s is not deployed into cluster %s.\n" % (service, cluster)
        returncode = 1

    sys.exit(returncode)