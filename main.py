import json
import logging
from time import sleep
import os
from datetime import date

import gi
gi.require_version('Gdk', '3.0')

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
import subprocess

logger = logging.getLogger(__name__)

#loglib="/home/qwxlea/Documents/Logseq/"

class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()

        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())
class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        items = []

        logger.info('preferences %s' % json.dumps(extension.preferences))
        logseq_path = extension.preferences['logseq_path']
        setting_limit = extension.preferences['setting_limit']

        jason={}
        jason["entries"]=[]

        inbox=os.path.join(logseq_path,"pages/Inbox.md")
        with open(inbox) as f:
            for index, line in enumerate(f):
                item={}
                item["line"]=line
                jason["entries"].append(item)


        query = event.get_argument() or ""
        split_query = query.partition(" ")

        keyword = split_query[0]

        if keyword != "":

            if keyword=="t".lower():
                items.append(ExtensionResultItem(icon='images/logo.png',
                                                name="Press enter to add: %s 📅" % (query[2:]),
                                                highlightable=False,
                                                on_enter=ExtensionCustomAction(query, keep_app_open=True)))
            elif keyword=="l".lower():
                items.append(ExtensionResultItem(icon='images/logo.png',
                                                name="Press enter to add: 'LATER %s' 📅" % (query[2:]),
                                                highlightable=False,
                                                on_enter=ExtensionCustomAction(query, keep_app_open=True)))
            else:
                items.append(ExtensionResultItem(icon='images/logo.png',
                                                name="Press enter to add (Inbox): %s" % (query),
                                                highlightable=False,
                                                on_enter=ExtensionCustomAction(query, keep_app_open=True)))

            return RenderResultListAction(items)

        else:

            for i in jason['entries']:
                item_line = i['line'][2:]

                items.append(ExtensionResultItem(icon='images/logo.png',
                                                 name='%s' % item_line,
                                                 description="", 
                                                 highlightable=False,
                                                 on_enter=DoNothingAction()
                                                 )
                            )

            return RenderResultListAction(items)

class ItemEnterEventListener(EventListener):

    def on_event(self, event, extension):

        items = []

        logger.info('preferences %s' % json.dumps(extension.preferences))
        logseq_path = extension.preferences['logseq_path']
        setting_limit = extension.preferences['setting_limit']

        data = event.get_data()
        if data[:2].lower()=="t ":
            ftarget=os.path.join(logseq_path,"journals",date.today().strftime("%Y-%m-%d.md"))
            data=data[2:]
            msg="'{}' to today's entry".format(data)
        elif data[:2].lower()=="l ":
            ftarget=os.path.join(logseq_path,"journals",date.today().strftime("%Y-%m-%d.md"))
            data="LATER {}".format(data[2:])
            msg="'{}' to today's entry".format(data)
        else:
            ftarget=os.path.join(logseq_path,"pages/Inbox.md")
            msg="'{}' to your inbox".format(data)

        with open(ftarget, "a") as f:
            last = subprocess.check_output(['tail', '-1', ftarget])
            if last!="-":
                f.write("\n- ")
            f.write(data)
        #FIXME: where to get a return value for a file write?
        rc = 0

        if rc == 0:
            items.append(ExtensionResultItem(icon='images/logo.png',
                                                name="Added %s" % msg,
                                                description='Press enter to exit',
                                                highlightable=False,
                                                on_enter=HideWindowAction()))
            return RenderResultListAction(items)
        else:
            items.append(ExtensionResultItem(icon='images/logo.png',
                                                            name="An error occurred",
                                                            description='Press enter to exit',
                                                            highlightable=False,
                                                            on_enter=HideWindowAction()))
        return RenderResultListAction(items)



if __name__ == '__main__':
    DemoExtension().run()
