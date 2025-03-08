We strive for some modularity.

We have he `src/fastergerman/web` module, then the `src/fastergerman/ui` module.
We should be able to delete the `ui` module and successfully run the `web` module and vice versa.
To achieve the above, `ui` libraries like `tkinter` should be limited to the `ui` module.

We delete the `ui` module, `tests` e.t.c before deploying to aws. If the `ui` module is present,
the deployment to ebs will fail with error: `ModuleNotFoundError: No module named 'tkinter'`.

Within the `web` module, web related imports like flask `request` and `session` are only
used from within the `request_data.py` file.

TODO - Implement architecture checks/tests.

