export function resolvePostAuthPath(query) {
  const redirect = query && query.redirect
  if (typeof redirect !== 'string' || !redirect.startsWith('/') || redirect.startsWith('//')) {
    return '/'
  }
  return redirect
}
