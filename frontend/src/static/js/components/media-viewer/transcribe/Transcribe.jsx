import React, { useEffect, useRef, useState } from 'react';
import i18next from 'i18next';
import { BrowserCache } from '../../../utils/classes/';
import getRegExp from '../../../utils/helpers/regex';
import { config } from '../../../utils/settings/config.js';
import './Transcribe.scss';
import { MediaPageStore } from '../../../utils/stores';

export default function Transcribe({ player }) {
  // storage
  const mediacms_config = config(window.MediaCMS);
  const browserCache = new BrowserCache(mediacms_config.site.id, 86400 * 365);

  // state
  const initInUse = browserCache.get('transcribe-in-use');
  const [inUse, setInUse] = useState(initInUse == undefined ? true : initInUse);
  const [track, setTrack] = useState(undefined);
  const [activeCue, setActiveCue] = useState(undefined);
  const [watchedCues, setWatchedCues] = useState([]);
  const [clipped, setClipped] = useState({});

  // ref
  const transcriptRef = useRef(null);
  const searchRef = useRef(null);

  const onPlayerLoadMetadata = (_) => {
    Array.from(player.textTracks()).forEach((track) => {
      if (track.mode == 'showing') {
        setTrack(track);
      }
    });
  };

  let lastTimeupdated = 0;
  const onPlayerTimeUpdate = (_) => {
    if (!track || !track.cues) {
      return;
    }

    const currentTime = player.currentTime();
    const flooredTime = Math.floor(currentTime);
    if (lastTimeupdated === flooredTime) {
      return;
    }
    lastTimeupdated = flooredTime;

    const watch = MediaPageStore.get('media-watch');
    const duration = player.duration();
    const _watchedCues = [];

    Array.from(track.cues).forEach((cue, i, arr) => {
      if (cue.startTime <= currentTime && currentTime <= cue.endTime) {
        setActiveCue(cue);
      }

      const endTime = arr.length - 1 == i ? Math.floor(duration) : arr[i + 1].startTime;
      const cueSeconds = watch.watched.slice(cue.startTime, endTime);

      if (cueSeconds && cueSeconds.length == endTime - cue.startTime) {
        // clean
        for (let j = 0; j < cueSeconds.length; j++) {
          cueSeconds[j] = cueSeconds[j] ? 1 : 0;
        }

        if (cueSeconds.every((e) => e)) {
          _watchedCues[i] = 1;
        }
      }
    });
    setTimeout(() => setWatchedCues(_watchedCues), 1);
  };

  const onLanguageChange = (e) => {
    Array.from(player.textTracks()).forEach((track) => {
      if (track.language == e.target.value) {
        setTrack(track);
      }
      setTimeout(function () {
        onTextSearch({ target: { value: searchRef.current.value } });
      }, 0);
    });
  };

  const onTranscriptClick = (e) => {
    if (e.target.classList.contains('clip')) {
      return;
    }

    const start = parseInt(e.target.parentElement.dataset.start, 10);
    if (start != undefined) {
      player.currentTime(start);
      player.play();
    }
  };

  const onInUseChange = (e) => {
    setInUse(e.target.checked);
  };

  const onTextSearch = (e) => {
    if (!transcriptRef.current) {
      return;
    }

    let pattern = e.target.value.replace(/\s/g, '');
    if (pattern) {
      pattern = getRegExp(pattern, {
        ignoreSpace: true,
        ignoreCase: true,
        global: true,
      });
    }

    transcriptRef.current.children.forEach((cueline) => {
      const textEl = cueline.querySelector('.text');

      // initialize
      let text = textEl.innerHTML.replace(/<\/?highlight>/g, '');
      let display = 'flex';

      if (pattern) {
        if (text.match(pattern)) {
          // highlight
          text = text.replace(pattern, function (matched) {
            return `<highlight>${matched}</highlight>`;
          });
        } else {
          display = 'none';
        }
      }

      textEl.innerHTML = text;
      cueline.style.display = display;
    });
  };

  const onClipChange = (e) => {
    const watch = MediaPageStore.get('media-watch');
    const cue = e.target.parentElement;
    const start = cue.dataset.start || 0;
    let text = null;

    if (e.target.checked) {
      text = cue.querySelector('.text').textContent;
      text = text.length > 20 ? `${text.slice(0, 20)}...` : text;
      clipped[start] = text;
      watch.clipped[start] = text;
    } else {
      delete clipped[start];
      delete watch.clipped[start];
    }
    setClipped({ ...clipped });
  };

  const formatDuration = (startTime) => {
    const date = new Date(1000 * startTime);
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    const seconds = date.getUTCSeconds().toString().padStart(2, '0');
    return `${minutes}:${seconds}`;
  };

  useEffect(() => {
    const watch = MediaPageStore.get('media-watch');
    setClipped({ ...watch.clipped });
  }, []);

  useEffect(() => {
    player.on('loadedmetadata', onPlayerLoadMetadata);
    player.on('timeupdate', onPlayerTimeUpdate);

    return () => {
      player.off('loadedmetadata', onPlayerLoadMetadata);
      player.off('timeupdate', onPlayerTimeUpdate);
    };
  }, [track]);

  useEffect(() => {
    // scroll vertical center
    const box = transcriptRef.current;
    const cueline = document.querySelector('.transcribe .active-cue');

    if (box && cueline) {
      if (cueline.style.display == 'none') {
        return;
      }

      box.scrollTo({
        top: cueline.offsetTop - box.offsetTop - box.offsetHeight / 2 + cueline.offsetHeight,
        left: 0,
        behavior: 'smooth',
      });
    }
  }, [activeCue]);

  useEffect(() => {
    const box = transcriptRef.current;
    if (box) {
      box.addEventListener('click', onTranscriptClick);
    }
    return () => {
      if (box) {
        box.removeEventListener('click', onTranscriptClick);
      }
    };
  }, [transcriptRef.current, inUse]);

  useEffect(() => {
    browserCache.set('transcribe-in-use', inUse);
  }, [inUse]);

  return (
    <>
      {track && (
        <div className="transcribe">
          <div className="control">
            {inUse && (
              <div>
                <select value={track.language} onChange={onLanguageChange}>
                  {Array.from(player.textTracks())
                    .filter((track) => track.language)
                    .map((track) => (
                      <option key={track.language} value={track.language}>
                        {track.label || track.language}
                      </option>
                    ))}
                </select>
                <input
                  className="search"
                  placeholder={i18next.t('Search in content')}
                  onChange={onTextSearch}
                  ref={searchRef}
                />
              </div>
            )}
            <div>
              <label className="checkbox-label right-selectbox" tabIndex={0}>
                {i18next.t('TRANSCRIBE IN USE')}
                <span className="checkbox-switcher-wrap">
                  <span className="checkbox-switcher">
                    <input type="checkbox" tabIndex={-1} checked={inUse} onChange={onInUseChange} />
                  </span>
                </span>
              </label>
            </div>
          </div>
          {inUse && track.cues && (
            <ul className="transcript" ref={transcriptRef}>
              {Array.from(track.cues).map((cue, i) => (
                <li
                  className={`cueline ${cue == activeCue ? 'active-cue' : ''} ${watchedCues[i] ? 'watched' : ''}`}
                  key={i}
                  data-start={cue.startTime}
                >
                  <span className="cuetimestamp">{formatDuration(cue.startTime)}</span>
                  <span className="text" dangerouslySetInnerHTML={{ __html: cue.text }}></span>
                  <input
                    className="clip"
                    type="checkbox"
                    onChange={onClipChange}
                    title={i18next.t('When checkbox checked, current position is clipped.')}
                    checked={!!clipped[cue.startTime]}
                  />
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </>
  );
}
