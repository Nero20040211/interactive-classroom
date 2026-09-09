# Long-course Navigation Contract 

The offline shell provides chapter/concept search, a current-scene bookmark button, a bookmarks-only filter, and a bibliography dialog. Search filters the scene navigator and must not re-render the current lesson. Bookmarks live only in runtime memory; closing/reloading the HTML resets them unless the user explicitly requests a persistence layer.

Navigation aids do not count toward progress/mastery. Scene navigation preserves the established scroll-state contract; in-scene interactions remain position-stable.
