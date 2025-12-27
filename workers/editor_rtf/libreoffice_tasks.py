#auxiliar/workers/libreoffice_tasks.py
from workers.base.base_task import BaseTask
from auxiliar.editor_texto.editor_externo import editar_rtf_con_libreoffice

def editar_rtf_task(rtf):
    return editar_rtf_con_libreoffice(rtf)