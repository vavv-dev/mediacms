import React from 'react';
import i18next from 'i18next';
import { format } from 'timeago.js';
import { useItem } from '../../utils/hooks/';
import { PositiveIntegerOrZero } from '../../utils/helpers/';
import { PlaylistItemMetaDate } from './includes/items/';
import { Item } from './Item';
import { selected as langSelected } from '../../utils/languages';

export function PlaylistItem(props) {
  const type = 'playlist';

  const { titleComponent, thumbnailUrl, UnderThumbWrapper } = useItem({ ...props, type });

  function metaComponents() {
    const publishDate = format(new Date(props.publish_date), langSelected);
    const publishDateTime =
      'string' === typeof props.publish_date
        ? Date.parse(props.publish_date)
        : Date.parse(new Date(props.publish_date));

    return <PlaylistItemMetaDate dateTime={publishDateTime} text={i18next.t('Created',  {date: publishDate})} />;
  }

  return (
    <div className="item playlist-item">
      <div className="item-content">
        <a
          className={'item-thumb' + (!thumbnailUrl ? ' no-thumb' : '')}
          href={props.link}
          title={props.title}
          tabIndex="-1"
          aria-hidden="true"
          style={!thumbnailUrl ? null : { backgroundImage: "url('" + thumbnailUrl + "')" }}
        >
          <div className="playlist-count">
            <div>
              <div>
                <span>{props.media_count}</span>
                <i className="material-icons">playlist_play</i>
              </div>
            </div>
          </div>

          <div className="playlist-hover-play-all">
            <div>
              <div>
                <i className="material-icons">play_arrow</i>
                <span>PLAY ALL</span>
              </div>
            </div>
          </div>
        </a>

        <UnderThumbWrapper title={props.title} link={props.link}>
          {titleComponent()}
          {metaComponents()}
          <a href={props.link} title="" className="view-full-playlist">
            {i18next.t("VIEW FULL PLAYLIST")}
          </a>
        </UnderThumbWrapper>
      </div>
    </div>
  );
}

PlaylistItem.propTypes = {
  ...Item.propTypes,
  media_count: PositiveIntegerOrZero,
};

PlaylistItem.defaultProps = {
  ...Item.defaultProps,
  media_count: 0,
};
