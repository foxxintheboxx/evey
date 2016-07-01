


class FBAPI(object):
    def make_button(self, type_, title, payload):
        dict_ = {"type": type_,
                 "title": title}
        if type_ == "web_url":
            dict_["url"] = payload
        if type_ == "postback":
            dict_["payload"] = payload
        return dict_

    def make_generic_element(self, title, subtitle="",
                                    img_url="",
                                    buttons=[]):
        element = {"title": title}
        if len(subtitle) > 0:
            element["subtitle"] = subtitle
        if len(img_url) > 0:
            element["image_url"] = img_url
        if len(buttons) > 0:
            element["buttons"] = buttons
        return element

    def generic_attachment(self, elements):
        return {"attachment": {
                  "type": "template",
                  "payload": {
                    "template_type": "generic",
                    "elements": elements
                    }
                  }
                }

    def text_message(self, text):
      return {"text": text}

    def button_attachment(self, text, buttons):
        return {"attachment": {
                  "type": "template",
                  "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": buttons
                  }
                }
              }

    def quick_reply(self, title, payload, type_="text"):
        return {"content_type": type_,
                "payload": payload,
                "title": title}

    def quick_replies(self, quick_replies, button_attachment=None, text=None):
        obj = None
        if button_attachment:
            button_attachment["quick_replies"]  = quick_replies
            obj = button_attachment
        if text:
            text["quick_replies"] = quick_replies
            obj = text
        return obj

