# Changelog

## v1.0
*  Rewrote in Django and Celery
  * Use Django to take advantage of more robust ORM and admin site.
  * Use Celery for writing configuration files to Prometheus nodes. This allows
    us to decouple the Promgen webui from the Prometheus nodes themselves and
    gives us better auditing when writing out the configuration files.
  * Support for using Celery to send out notifications instead of blocking a
    single thread
  * Optionally use Sentry for debugging exceptions from within Promgen
  * Take advantage of Python's setuptools endpoints for easier plugin management
* [IMPROVEMENT] Senders can be set for both Projects and Services
* [IMPROVEMENT] Improved rule editor
  * More easily edit labels and annotations on rules
  * Button to test query against Prometheus to help testing
* [IMPROVEMENT] Shard support. Supports assigning services to different shards
  for capacity management
* [IMPROVEMENT] Better support for writing sender plugins by using Python's
  setuptools framework
* [IMPROVEMENT] Blackbox exporter support by adding URLs to Project pages
* [IMPROVEMENT] Support toggling Rules and Exporters
