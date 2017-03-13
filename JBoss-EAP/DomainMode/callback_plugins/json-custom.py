# (c) 2016, Matt Martz <matt@sivel.net>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os
import sys
import shutil
import glob
# sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../python-routines/asciidoctorgenerator.py")
# from asciidoctorgenerator import *

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    # CALLBACK_VERSION = 2.0
    # CALLBACK_TYPE = 'stdout'
    # CALLBACK_NAME = 'json'

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'json-custom'
    CALLBACK_NEEDS_WHITELIST = True
    # PATH_REPORT=os.path.dirname(os.path.abspath(__file__));

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display)
        self.results = []

    def _new_play(self, play):
        return {
            'play': {
                'name': play.name,
                'id': str(play._uuid)
            },
            'tasks': []
        }

    def _new_task(self, task):
        return {
            'task': {
                'name': task.name,
                'id': str(task._uuid)
            },
            'hosts': {}
        }

    def v2_playbook_on_play_start(self, play):
        self.results.append(self._new_play(play))

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.results[-1]['tasks'].append(self._new_task(task))

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        self.results[-1]['tasks'][-1]['hosts'][host.name] = result._result

    def v2_playbook_on_stats(self, stats):
        """Display info about playbook statistics"""

        hosts = sorted(stats.processed.keys())

        summary = {}
        for h in hosts:
            s = stats.summarize(h)
            summary[h] = s

        output = {
            'plays': self.results,
            'stats': summary
        }

        print(json.dumps(output, indent=4, sort_keys=True))
        facts_location=os.path.dirname(os.path.abspath(__file__))+ "/../documentation/";
        facts_file=facts_location+"play-data.json"
        if not os.path.exists(facts_location):
            os.makedirs(facts_location)
        with open(facts_file, "w") as text_file:
            text_file.write(json.dumps(output, indent=4, sort_keys=True))
        self.asciidoctorgenerator(output)

    def asciidoctorgenerator(self, facts):
        print("ENTRANDO A generate-asciidoc()")
        # facts_file=os.path.dirname(os.path.abspath(__file__))+ "/../documentation/test.json"
        result_folder=os.path.dirname(os.path.abspath(__file__))+ "/../results/";

        checklist_data = dict()
        checklist_file_list = []
        checklist_data_list = []

        for item in facts['plays']:
            for f in glob.glob(result_folder+"data/*"):
                archivo = f.split("/")
                nombre=(archivo[len(archivo)-1]).split("-")
                nombreArchivo1=nombre[0]
                nombreArchivo2=item['play']['name']
                if nombreArchivo1 == nombreArchivo2:
                 print("eliminando archivo -->"+ item['play']['name'])
                 os.remove(f)
            # Generar nuevo archivo
            fname=result_folder+"data/"+item['play']['name']+"-"+item['play']["id"]+".adoc"

            with open(fname, "w") as text_file:
                self.printLine(text_file, "=== Grupo: "  +item['play']['name'])
                self.printLine(text_file,"\n ");
                tasksName = list()
                for task in item['tasks']:
                    if task['task']['name']:
                        tasksName.append(task['task']['name'])
                        self.printLine(text_file,"==== TASK: "+ task['task']['name'])
                        for host,invhost in task['hosts'].iteritems():
                            # print(invhost)
                            raw_cmd =invhost['invocation']['module_args']['_raw_params']
                            self.printLine(text_file,"."+host)
                            if "cat {}" not in raw_cmd:
                                self.printLine(text_file,"[source,bash]")
                                self.printLine(text_file,"----")
                                self.printLine(text_file,"$ "+ str(raw_cmd))
                                if invhost['stdout_lines']:
                                    for line in invhost['stdout_lines']:
                                        self.printLine(text_file, str(line))
                                else:
                                    self.printLine(text_file, invhost['stderr'])
                                self.printLine(text_file,"----")
                                self.printLine(text_file,"\n ");
                            else:
                                self.printLine(text_file,"[source,bash]")
                                self.printLine(text_file,"----")
                                self.printLine(text_file,"$ "+ str(raw_cmd))
                                self.printLine(text_file,"----")
                                self.printLine(text_file,"\n ");
                                #seccion de archivos
                                self.printLine(text_file,"====")
                                if invhost['stdout_lines']:
                                    for line in invhost['stdout_lines']:
                                        self.printLine(text_file, str(line))
                                else:
                                    self.printLine(text_file, invhost['stderr'])
                                self.printLine(text_file,"\n ");
                                #fin seccion de archivos
                checklist_data[item['play']['name']] = tasksName;
                checklist_folder=result_folder+"checklists/"

                for key, value in checklist_data.iteritems():
                    chkfilename=checklist_folder+"anexo_"+key+".adoc"
                    checklist_file_list.append("checklists/anexo_"+key+".adoc")

                    print(checklist_file_list)
                    with open(chkfilename, "w") as chkfile:
                        self.printLine(chkfile,"=== Producto: "+key)
                        self.printLine(chkfile,"\n")
                        self.printLine(chkfile,"====")
                        self.printLine(chkfile,".Checklist "+key)
                        self.printLine(chkfile,"//[width=\"100%\", cols=\"^1,^1,4,16\", frame=\"topbot\",options=\"header\"]")
                        self.printLine(chkfile,"[width=\"100%\", cols=\"^1,4,4\", frame=\"topbot\",options=\"header\"]")
                        self.printLine(chkfile,"|======================")
                        self.printLine(chkfile,"//| #        \n//| Res \n//| Aspecto    \n//| Comentario")
                        self.printLine(chkfile,"| #        \n| Aspecto    \n| Comprobacion")
                        self.printLine(chkfile,"\n")
                        cont = 0
                        for taskItem in value:
                            cont = cont + 1
                            # self.printLine(chkfile, ""+str(taskItem))
                            # print str.replace("is", "was")
                            self.printLine(chkfile,"| "+str(cont))
                            self.printLine(chkfile,"//| image:w.png[]")
                            self.printLine(chkfile,"| "+str(taskItem).replace("|", "\|"))
                            self.printLine(chkfile,"| TBD")
                            self.printLine(chkfile,"\n")

                        self.printLine(chkfile,"|======================")
                        self.printLine(chkfile,"====")

        ## Armando listado con archivos data para el anexos.adoc
        for f in glob.glob(result_folder+"data/*"):
            archivo = f.split("/")
            print(archivo[len(archivo)-1])
            checklist_data_list.append(archivo[len(archivo)-2]+"/"+archivo[len(archivo)-1])

        ## Creando archivo de anexos: data
    #    fname=result_folder+"1_anexos_checklist.adoc"

    #    with open(fname, "w") as chkfile:
    #        self.printLine(chkfile,"== Anexo: Checklist de puntos ")
    #        for item in set(checklist_file_list):
    #            if "INIT" not in item:
    #                self.printLine(chkfile,"\n")
    #                self.printLine(chkfile,"include::"+item+"[]")
    #            # checklist_file_list.append("checklists/anexo_"+key+".adoc")
        fname=result_folder+"2_anexos_data.adoc"
        with open(fname, "w") as chkfile:
            self.printLine(chkfile,"== Anexo: Datos obtenidos ")
            for item in set(checklist_data_list):
                if "INIT" not in item:
                    self.printLine(chkfile,"\n")
                    self.printLine(chkfile,"include::"+item+"[]")

    def str_unicode(self,text):
        try:
            text = unicode(text, 'utf-8')
        except TypeError:
            return text

    def printLine(self,file, texto):
        print("PRINT LINE: "+ texto)
        file.write(texto+"\n");


    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_unreachable = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok
