# Interview points

- **Why dependency order matters:** screening a customer whose
  identity step never passed produces a confident-looking result
  about the wrong person. Ordering is enforced by raising, not by
  documentation.
- **Why re-grounding beats chaining text:** if each step consumes the
  previous step's output, small errors compound. Re-reading the
  source record at each step bounds the error to one step, and the
  drift check turns a contradiction into a visible failure.
- **Why fuzzy hits escalate instead of rejecting:** a similarity
  score is not an identity match. Auto-rejecting on it would punish
  people who share a similar name; escalating spends reviewer time
  where uncertainty is highest.
- **Why the authorizer, not a wrapper:** a helper function that
  "only reads views" can be bypassed by any caller who forgets it.
  SQLite's authorizer denies the query itself, so the rule holds for
  every caller on that connection.
- **Why tests assert exception types, not messages, for the
  authorizer:** the denial text belongs to SQLite. Asserting on it
  would couple the suite to an implementation detail and give false
  confidence if the text changed.
- **A bug I found and fixed:** an escalated step blocked the rest of
  the chain, and demo state leaked between customers. Both became
  regression tests instead of being quietly patched.
- **What I would not claim:** screening accuracy, regulatory
  compliance, or calibrated risk. The data is synthetic and the
  sample (4 demo customers, 80 regression checks) cannot support
  those claims.
