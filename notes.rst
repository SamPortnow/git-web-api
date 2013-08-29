Repos
=====

Create
   * PUT to /
       * on success
           * url to the /<r>/
       * on failure
           * 400-series status code

Read (repo-level meta information)
    * on success
        * Settings
            * Public/Private
            * allowed users []
            * synced remotes []
        * Meta
            * file tree
            * created date
            * access level of current authentication context

Update (change settings)
    * on success
        * HTTP 200
    * on failure
        * 400-series status code
        * each request is atomic

Delete
    * on success
        * HTTP 200
    * on failure
        * 400-series status code



Files
=====

Create
    * PUT to /<r>/
        * Infers filename from the file, or from data passed in request
    * PUT to /<r>/<f>
        * Uses filename and path specified in URL


Read
    * GET to /<r>/<f>

Update
    * POST to /<r>/<f> with new version of the file

Delete
    * DELETE to /<r>/<f>



Global
======

Return dict containing URL on success.

On failure, return { 'message': 'asdfasdfasdfasdfasdf' }
