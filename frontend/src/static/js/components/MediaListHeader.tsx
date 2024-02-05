import React from 'react';
import i18next from 'i18next';

interface MediaListHeaderProps {
  title?: string;
  viewAllLink?: string;
  viewAllText?: string;
  className?: string;
  style?: { [key: string]: any };
}

export const MediaListHeader: React.FC<MediaListHeaderProps> = (props) => {
  const viewAllText = i18next.t(props.viewAllText || 'VIEW ALL');
  return (
    <div className={(props.className ? props.className + ' ' : '') + 'media-list-header'} style={props.style}>
      <h2>{i18next.t(props.title || '')}</h2>
      {props.viewAllLink ? (
        <h3>
          {' '}
          <a href={props.viewAllLink} title={viewAllText}>
            {' '}
            {viewAllText || props.viewAllLink}{' '}
          </a>{' '}
        </h3>
      ) : null}
    </div>
  );
};
