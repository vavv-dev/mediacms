import i18next from 'i18next';
import { register } from 'timeago.js';
import ko from 'timeago.js/lib/lang/ko';
import { enabled as langEnabled, selected as langSelected, translations as langTranslations } from '.';

register('ko', ko);

const resources: {
  [key: string]: {
    translation: { [key: string]: string };
  };
} = {};

for (let k in langEnabled) {
  resources[langEnabled[k]] = { translation: langTranslations[langEnabled[k]] };
}

function translateByTextContent(selector: string, text: string, t: (key: string) => string): void {
  var elements = document.querySelectorAll(selector);
  for (var i = 0; i < elements.length; i++) {
    if ((elements[i].textContent as string | null)?.trim() === text) {
      elements[i].innerHTML = t(text);
      return;
    }
  }
}

i18next.init(
  {
    resources,
    lng: langSelected,
    fallbackLng: langSelected,
    interpolation: {
      escapeValue: false,
    },
  },
  (err, t) => {
    try {
      // TODO user react-i18next
      setTimeout(() => {
        translateByTextContent('h1', 'Upload media files', t);
        // translateByTextContent('span', 'Drag and drop files', t);
        // translateByTextContent('span', 'Browse your files', t);
      }, 0);
    } catch (e) {
      console.error(e);
    }
  }
);

export default i18next;
